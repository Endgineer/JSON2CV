from compiler.units.Item import Item

PARAGRAPH = 'paragraph'
CATEGORY = 'category'
CONTENT = 'content'
TITLE = 'title'
SUBTITLE = 'subtitle'
BTAG = 'btag'
TTAG = 'ttag'
LTAG = 'ltag'
RTAG = 'rtag'
DETAILS = 'details'
LABELS = 'labels'

STRS = { PARAGRAPH, CATEGORY, CONTENT, TITLE, SUBTITLE, BTAG, TTAG, LTAG, RTAG }
LISTS = { DETAILS }
DICTS = { LABELS }

CVGLOBALS_REQUIRED = set()
CVGLOBALS_OPTIONAL = { LABELS }

CVPARAGRAPH_REQUIRED = CVGLOBALS_REQUIRED.union({ PARAGRAPH })
CVPARAGRAPH_OPTIONAL = CVGLOBALS_OPTIONAL.union(set())
CVPARAGRAPH = set.union(CVPARAGRAPH_REQUIRED, CVPARAGRAPH_OPTIONAL)

CVSKILLS_REQUIRED = CVGLOBALS_REQUIRED.union({ CATEGORY, CONTENT })
CVSKILLS_OPTIONAL = CVGLOBALS_OPTIONAL.union(set())
CVSKILLS = set.union(CVSKILLS_REQUIRED, CVSKILLS_OPTIONAL)

CVENTRIES_REQUIRED = CVGLOBALS_REQUIRED.union({ TITLE, SUBTITLE, BTAG, TTAG })
CVENTRIES_OPTIONAL = CVGLOBALS_OPTIONAL.union({ DETAILS })
CVENTRIES = set.union(CVENTRIES_REQUIRED, CVENTRIES_OPTIONAL)

CVHONORS_REQUIRED = CVGLOBALS_REQUIRED.union({ TITLE, SUBTITLE, LTAG, RTAG })
CVHONORS_OPTIONAL = CVGLOBALS_OPTIONAL.union(set())
CVHONORS = set.union(CVHONORS_REQUIRED, CVHONORS_OPTIONAL)

ALL_REQUIRED = set.union(CVPARAGRAPH_REQUIRED, CVSKILLS_REQUIRED, CVENTRIES_REQUIRED, CVHONORS_REQUIRED)
ALL_OPTIONAL = set.union(CVPARAGRAPH_OPTIONAL, CVSKILLS_OPTIONAL, CVENTRIES_OPTIONAL, CVHONORS_OPTIONAL)
ALL = set.union(ALL_REQUIRED, ALL_OPTIONAL)

def prop_similarity_coefficients(props: set[str]) -> dict[Item.Kind, float]:
  '''
  Returns the Jaccard similarity coefficient of the 'props' set against each prop set type. A perfect similarity with a set type implies that 'props':
  \n* Contains all required props of that set type
  \n* May or may not contain any optional props of that set type
  \n* Does not contain any other prop irrelevant to that set type
  '''
  return {
    Item.Kind.CVPARAGRAPH: float(len(CVPARAGRAPH_REQUIRED.intersection(props - CVPARAGRAPH_OPTIONAL))) / float(len(CVPARAGRAPH_REQUIRED.union(props - CVPARAGRAPH_OPTIONAL))),
    Item.Kind.CVSKILLS: float(len(CVSKILLS_REQUIRED.intersection(props - CVSKILLS_OPTIONAL))) / float(len(CVSKILLS_REQUIRED.union(props - CVSKILLS_OPTIONAL))),
    Item.Kind.CVENTRIES: float(len(CVENTRIES_REQUIRED.intersection(props - CVENTRIES_OPTIONAL))) / float(len(CVENTRIES_REQUIRED.union(props - CVENTRIES_OPTIONAL))),
    Item.Kind.CVHONORS: float(len(CVHONORS_REQUIRED.intersection(props - CVHONORS_OPTIONAL))) / float(len(CVHONORS_REQUIRED.union(props - CVHONORS_OPTIONAL))),
  }