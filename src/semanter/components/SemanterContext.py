import logging
import os

from parser.Parser import Parser
from compiler.units.Item import Item
from compiler.units.Prop import Prop
import semanter.constants.propset as propset
from semanter.utilities.IdentifierVerifier import IdentifierVerifier

class SemanterContext:
  parser: Parser
  cache: dict[str, dict[str, Item] | None]
  registry: dict[str, Item.Kind]
  current_item_valid: bool
  identifier_verifier: IdentifierVerifier

  def __init__(self, parser: Parser):
    self.parser = parser
    self.cache = dict()
    self.registry = dict()
    self.current_item_valid = True
    self.identifier_verifier = IdentifierVerifier()



  def analyze_item(self, item: Item) -> Item:
    if item is None: return None

    self.current_item_valid = True
    item.kind = None
    item.labels = None

    analyzable_props = self.analyze_prop_keys(item)
    analyzable_props = self.analyze_prop_vals(analyzable_props)
    labels = self.analyze_prop_labels(analyzable_props)

    if self.analyze_item_registration(item, labels):
      return item



  def error(self, message: str) -> None:
    logging.getLogger('SEMANTIC').error(message)
    self.current_item_valid = False



  def analyze_prop_keys(self, item: Item) -> list[Prop]:
    props_with_valid_keys = list()

    key_registry = dict()
    for property in item.properties:
      if property.key is None:
        continue

      if property.key.get_string() in propset.ALL:
        if property.value is not None:
          props_with_valid_keys.append(property)
      else:
        self.error(f'Invalid prop key {property.key}.')

      if property.key.get_string() in key_registry:
        self.error(f'Duplicate prop key {property.key}, previously found {key_registry[property.key.get_string()]} other(s).')
        key_registry[property.key.get_string()] += 1
      else:
        key_registry[property.key.get_string()] = 1
    
    item_kind_probabilities = propset.prop_similarity_coefficients(set(key_registry))
    for item_kind, probability in item_kind_probabilities.items():
      if probability == 1.0:
        item.kind = item_kind
        break
    
    if item.kind is None:
      self.error(f'Item {item} has an undeterminable type due to an invalid combination of props.')
    
    return props_with_valid_keys
  


  def analyze_prop_vals(self, props_with_valid_keys: list[Prop]) -> list[Prop]:
    props_with_valid_keys_vals = list()

    for prop in props_with_valid_keys:
      if prop.kind == str:
        if prop.key.get_string() in propset.STRS:
          props_with_valid_keys_vals.append(prop)
        else:
          self.error(f'Prop key {prop.key} expected a value of type {str} instead of {prop.kind}.')
      elif prop.kind == list:
        if prop.key.get_string() in propset.LISTS:
          props_with_valid_keys_vals.append(prop)
        else:
          self.error(f'Prop key {prop.key} expected a value of type {list} instead of {prop.kind}.')
      elif prop.kind == dict:
        if prop.key.get_string() in propset.DICTS:
          props_with_valid_keys_vals.append(prop)
        else:
          self.error(f'Prop key {prop.key} expected a value of type {dict} instead of {prop.kind}.')
    
    return props_with_valid_keys_vals
  


  def analyze_prop_labels(self, props_with_valid_keys_vals: list[Prop]) -> dict[str, str]:
    label_registry = dict()
    
    for prop in props_with_valid_keys_vals:
      if prop.key.get_string() == propset.LABELS:
        for pair in prop.value:
          pair_key = pair[0].get_string()
          if pair_key in label_registry:
            self.error(f'Duplicate label {pair[0]}, previously found {label_registry[pair_key]} other(s).')
            label_registry[pair_key] += 1
          else:
            label_registry[pair_key] = 1
          
          pair_key_cycle = pair[0].contains_invocation()
          pair_val_cycle = pair[1].contains_invocation()

          if pair_key_cycle:
            self.error(f'Label key {pair[0]} cannot contain an invocation.')
          if pair_val_cycle:
            self.error(f'Label value {pair[0]} cannot contain an invocation.')
    
    return label_registry



  def analyze_item_registration(self, item: Item, labels: dict[str, str]) -> bool:
    section_name = item.section.get_string()

    if section_name.strip() == '':
      self.error(f'Section namespace {item.section} cannot be nameless.')
    elif item.section.contains_invocation():
      self.error(f'Section namespace {item.section} cannot contain an invocation.')
    elif section_name in self.registry and self.registry[section_name] != item.kind:
      self.error(f'Type mismatch between item {item} and section namespace "{section_name}", which has previously accepted items of type {self.registry[section_name].name}.')
    elif self.current_item_valid:
      self.registry[section_name] = item.kind
      logging.getLogger('SEMANTIC').debug(f'Registered item {item} under section namespace "{section_name}".')
      item.labels = labels
      return True
    
    return False



  def fetch(self, item: Item, recursed: bool = False) -> Item:
    if item.reference.contains_invocation():
      return self.error(f'Item {item} cannot contain an invocation.')
    
    reference_parts = item.reference.get_string().split('::')

    if len(reference_parts) != 2:
      return self.error(f'Item {item} is not of the form "<FILE_BASENAME_PATH>::<ITEM_IDENTIFIER>".')
    
    fileref, itemref = reference_parts

    empty_ref = False
    if fileref.strip() == '':
      self.error(f'File basename path "{fileref}" in item {item} cannot be empty.')
      empty_ref = True
    if itemref.strip() == '':
      self.error(f'Item identifier "{itemref}" in item {item} cannot be empty.')
      empty_ref = True
    if empty_ref: return

    if not self.identifier_verifier(itemref):
      return self.error(f'Item identifier "{itemref}" in item {item} is not a valid identifier.')

    if not os.path.isfile(f'{fileref}.json'):
      return self.error(f'File path "{fileref}.json" from item {item} does not point to an existing file.')
    
    if fileref in self.cache:
      if self.cache[fileref] is None:
        return self.error(f'File reference "{fileref}" in {item} points to an invalid or empty file.')
      elif itemref in self.cache[fileref]:
        if not recursed: logging.getLogger('SEMANTIC').debug(f'Cache hit for item {item}.')
        return Item(item.section, self.cache[fileref][itemref].reference, item.line_number, item.char_number, self.cache[fileref][itemref].properties)
      else:
        return self.error(f'Item {item} does not exist in referenced file "{fileref}.json".')

    logging.getLogger('SEMANTIC').debug(f'Cache miss for item {item}.')
    
    file_items = self.parser.parse_all(f'{fileref}.json')
    self.cache[fileref] = dict()
    reference_registry = dict()

    for file_item in file_items:
      if file_item.reference.contains_invocation():
        self.error(f'The identifier of item {file_item} in file "{fileref}.json" cannot contain an invocation.')
        continue

      file_item_reference_string = file_item.reference.get_string()

      if file_item_reference_string.strip() == '':
        self.error(f'The identifier of item {file_item} in file "{fileref}.json" cannot be empty.')
        continue

      if not self.identifier_verifier(file_item_reference_string):
        self.error(f'The identifier of item {file_item} in file "{fileref}.json" is not a valid identifier.')
        continue

      if file_item_reference_string in reference_registry:
        self.error(f'Duplicate identifier of item {file_item} in file "{fileref}.json", previously found {reference_registry[file_item_reference_string]} other(s).')
        reference_registry[file_item_reference_string] += 1
        continue

      reference_registry[file_item_reference_string] = 1
      self.cache[fileref][file_item_reference_string] = file_item
    
    return self.fetch(item, True)