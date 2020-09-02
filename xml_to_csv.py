import os
import numpy as np
import pandas as pd
from collections import OrderedDict, defaultdict
import xmltodict
import argparse


def get_all_cols(x: OrderedDict, prefix: str='', page_set: set=None) -> set:
    """
    Iterates through a nested ordered dict and returns a set of columns which would be required
    for each "page" of data, where pages are "delimited" by the element tag "numerical data".

    Example data (based off of actual data for which this was used):

    OrderedDict([

             ('numerical data', '####'),
             ('string data', 'something'),

             ('nested OrderedDict',
              OrderedDict([('PrimaryClaimCauseOfAction',
                            OrderedDict([('CauseOfActionType', 'Non-Payment'),
                                         ('Amount', '####')]))])),

             ('nested OrderedDict with possible duplicate columns',
                  OrderedDict([('Party',
                               [OrderedDict([('Role', 'something else 1'),
                                             ('PartyType', 'something else 1'),
                                             ('RepresentationType', 'something else 1'),
                                             ('Undertenant', 'something else 1')]),
                                OrderedDict([('Role', 'something else 2'),
                                             ('PartyType', 'something else 2'),
                                             ('RepresentationType', 'something else 2'),
                                             ('Undertenant', 'something else 2')])])])),

             ('this is just a list because this data is bad',
              ['list item 1', 'list item 2'])

              ])

    The set output from this page of data is:

    {
    '/numerical data',
    '/string data',
    '/nested OrderedDict/PrimaryClaimCauseOfAction/CauseOfActionType',
    '/nested OrderedDict/PrimaryClaimCauseOfAction/Amount',
    '/nested OrderedDict with possible duplicate columns/Party/Role',
    '/nested OrderedDict with possible duplicate columns/Party/PartyType',
    '/nested OrderedDict with possible duplicate columns/Party/RepresentationType',
    '/nested OrderedDict with possible duplicate columns/Party/Undertenant',
    '/nested OrderedDict with possible duplicate columns/Party/Role_2',
    '/nested OrderedDict with possible duplicate columns/Party/PartyType_2',
    '/nested OrderedDict with possible duplicate columns/Party/RepresentationType_2',
    '/nested OrderedDict with possible duplicate columns/Party/Undertenant_2',
    '/this is just a list because this data is bad',
    }

    """
    if page_set is None:
        page_set = set()

    for i in x.items():
        if isinstance(i[1], OrderedDict):
            # If the data is an OrderedDict, then the funciton is called recursively until it is
            # not. Along the way, it prepends a prefix to show absolute path within the page.
            get_all_cols(i[1], prefix + '/' + i[0], page_set)
        elif isinstance(i[1], list):
            # If the data is a list (in this case, of OrderedDict objects), then the function is
            # called on all items in the list. The list of OrderedDicts will execute by the block
            # above unless they are themselves lists or simply what is effectively a 2-tuple of
            # strings.
            for item in i[1]:
                # Some data is a simple list of strings. When they get here, only items which
                # have an "items" attribute can be properly iterated by the top level loop. There
                # is a but of duck typing going on here, but it's a risk I'm willing to take.
                if hasattr(item, 'items'):
                    get_all_cols(item, prefix + '/' + i[0], page_set)
        else:
            if prefix + '/' + i[0] in page_set:
                for j in range(2,1000):
                    if prefix + '/' + i[0] + f'_{j}' in page_set:
                        pass
                    else:
                        page_set.add(prefix + '/' + i[0] + f'_{j}')
                        break
            else:
                page_set.add(prefix + '/' + i[0])
    return page_set

def create_data(x: OrderedDict, prefix: str='', page_df: pd.DataFrame=None, all_cols: set=None) -> pd.DataFrame:
    """
    Iterates through a possibly nested ordered dict (a "page") and returns the data
    from the page in a dataframe. A set with every possible column needs to be provided,
    hence the all_cols function.
    """
    if page_df is None:
        page_df = pd.DataFrame(np.empty((1,len(all_cols)), dtype=str), columns=all_cols)
    for i in x.items():
        if isinstance(i[1], OrderedDict):
            create_data(i[1], prefix + '/' + i[0], page_df)
        elif isinstance(i[1], list):
            for item in i[1]:
                if hasattr(item, 'items'):
                    create_data(item, prefix + '/' + i[0], page_df)
        else:
            if page_df[prefix + '/' + i[0]][0] != '':
                for j in range(2, 1000):
                    if page_df[prefix + '/' + i[0] + f'_{j}'][0] != '':
                        pass
                    else:
                        page_df[prefix + '/' + i[0] + f'_{j}'][0] = i[1]
                        break
            else:
                page_df[prefix + '/' + i[0]][0] = i[1]
    return page_df

def main(input: str, output: str, delim: str=','):
    if not input.endswith('.xml'):
        input += '.xml'
    if not output.endswith('.csv'):
        output += '.csv'
    with open(input, 'r') as f:
        """All of the data is actually stored in Extract/Indexes/Index of the parsed object.
        They are read in as list of (nested) ordered dict objects."""
        actual_data = xmltodict.parse(f.read())['Extract']['Indexes']['Index']

    all_cols = set()
    for i in actual_data:
        all_cols = all_cols.union(get_all_cols(i))

    df_output = pd.DataFrame(np.empty((len(actual_data),len(all_cols)), dtype=str), columns=all_cols)
    i = 0
    for page in actual_data:
        if not i % 1000:
            print(f"Beginning on the {i}th page of XML data.")
        df_output.iloc[i] = create_data(page, all_cols=all_cols).iloc[0]
        i += 1

    df_output.to_csv(output, sep=delim, index=False)

if __name__ == "__main__":
    """
    Format:\n
    arbitrary_nested_xml_to_df input[.xml] output[.csv]\n
    Examples:\n
    arbitrary_nested_xml_to_df my_annoying_xml my_better_csv\n\n
    arbitrary_nested_xml_to_df my_weird_xml.xml preferable_output.csv -d '|'\n\n
    """
    parser = argparse.ArgumentParser(
    description="Takes an XML and returns a CSV."
    )
    parser.add_argument(
    "input", help="""The destination of the input file,
    .xml extension is optional."""
    )
    parser.add_argument(
    "output", help="""The destination of the input file,
    .xml extension is optional."""
    )
    parser.add_argument(
    "-d", "--delimiter", type=str, choices=list(",;:|\t"), default=","
    )
    args = parser.parse_args()
    main(args.input, args.output, args.delimiter)
