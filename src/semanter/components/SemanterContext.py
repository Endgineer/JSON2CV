import logging
import os

from parser.Parser import Parser
from compiler.units.Item import Item
from compiler.units.Prop import Prop
import semanter.constants.propset as propset

class SemanterContext:
  parser: Parser
  cache: dict[str, dict[str, Item] | None]
  registry: dict[str, Item.Kind]
  current_item_valid: bool

  def __init__(self, parser: Parser):
    self.parser = parser
    self.cache = dict()
    self.registry = dict()
    self.current_item_valid = True



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
  


  def analyze_prop_labels(self, props_with_valid_keys_vals: list[Prop]) -> set[str]:
    label_registry = dict()
    
    for prop in props_with_valid_keys_vals:
      if prop.key.get_string() == 'labels':
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
    
    return set(label_registry)



  def analyze_item_registration(self, item: Item, labels: set[str]) -> bool:
    if item.section.strip() == '':
      self.error(f'Item {item} cannot belong to a nameless section.')
    
    if item.section in self.registry and self.registry[item.section] != item.kind:
      self.error(f'Type mismatch between item {item} and section "{item.section}", which has previously accepted items of type {self.registry[item.section].name}.')
    
    if self.current_item_valid:
      self.registry[item.section] = item.kind
      logging.getLogger('SEMANTIC').debug(f'Registered item {item} in section "{item.section}".')
      item.labels = labels
      return True
    
    return False



  def fetch(self, item: Item) -> Item:
    reference_parts = item.reference.split('::')

    if len(reference_parts) != 2:
      logging.getLogger('SEMANTIC').error(f'Item {item} is not of the form "<FILE_BASENAME_PATH>::<ITEM_IDENTIFIER>".')
      return None
    
    fileref, itemref = reference_parts

    if fileref in self.cache:
      if self.cache[fileref] is None:
        logging.getLogger('SEMANTIC').error(f'File reference "{fileref}" at line {item.line_number} position {item.char_number} points to an invalid file.')
        return None
      elif itemref in self.cache[fileref]:
        logging.getLogger('SEMANTIC').debug(f'Cache hit for item {item}.')
        return self.cache[fileref][itemref]
      else:
        logging.getLogger('SEMANTIC').error(f'Item {item} does not exist in referenced file "{fileref}.json".')
        return None

    if not os.path.isfile(f'{fileref}.json'):
      logging.getLogger('SEMANTIC').error(f'Reference "{fileref}.json::{itemref}" at line {item.line_number} position {item.char_number} does not point to an existing file.')
      return None
    
    logging.getLogger('SEMANTIC').debug(f'Cache miss for item {item}.')
    return None