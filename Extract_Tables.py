#!/usr/bin/env python

import os
import sys
import re
import pandas as pd
import math
import camelot
import dateutil
import click
import logging
import coloredlogs

from typing import List

coloredlogs.install('DEBUG')
logger = logging.getLogger()
logging.getLogger('pdfminer').setLevel('ERROR')
logging.getLogger('pandas').setLevel('ERROR')

class NoHeaderFound(ValueError): pass

class TableExtractor:
    def __init__(self, file_path, single_val_cols=None):
        """
        """
        self.path = file_path
        logger.debug(f'extracting tables from {self.path}')
        tables = camelot.read_pdf(self.path, flavor='stream', pages='all')
        logger.debug(f'{len(tables)} tables found')
        self.tables = [tab.df for tab in tables]

    def process_df(self, df: pd.DataFrame):
        logger.debug(f'processing table with shape {df.shape}')
        # header index
        h_row = self.find_header_row(df)
        headers = list(df.iloc[h_row,:]) # Column names
        logger.debug(f"Headers found: {headers}")
        # strip the top garbage values
        df = df.iloc[h_row+1:,:]
        # set the header
        df.columns = headers
        #  Find columns with single values. Occurance of these values indicate start of new row. eg. Amount and Date
        single_val_cols = self.get_single_val_cols(df)
        logger.debug(f"Single Value Columns: {single_val_cols}")
        # Any row that doesn't qualify for single_val_col can have multiline values and need row merging
        multi_val_cols = [c for c in df.columns if c not in single_val_cols]
        # Find starting index of rows
        starts = self.find_starting_rows(df, single_val_cols)
        # Merge multi_val_cols between the row boundries
        for i,j in zip(starts[:-1],starts[1:]):
            for m_col in multi_val_cols:
                                            # use only non empty string to merge
                df[m_col][i] = "\n".join([elem for elem in df[m_col].loc[i:j-1] if elem])

        # Drop the rows multicol text of which has been merged above them
        df = df.drop(set(df.index)-set(starts))
        # reset index
        df = df.reset_index(drop=True)
        logger.debug(f"Processed Table shape: {df.shape}")
        return df

    def valid_header(self, row: pd.Series):
        """A row is valid is all the cells elements are neither nan nor empty string"""
        for j,elem in row.items():
            # if empty string or nan, skip. check for float before calling isnan to avoid TypeError
            if not elem or (isinstance(elem, float) and np.isnan(elem)):
                return False
        return True

    def find_header_row(self, df:pd.DataFrame):
        for i,row in df.iterrows():
            if self.valid_header(row): return i
        raise NoHeaderFound('No Rows satisfy the valid header condition')

    @staticmethod
    def is_date(candidate):
        """Check if a candidate can be parsed by the dateparser. Not necessarily accurate"""
        try:
            _ = dateutil.parser.parse(candidate)
            return True
        except dateutil.parser.ParserError:
            return False

    @staticmethod
    def is_amount(candidate):
        """Is a valid amount.
        Doesn't support european way of writing the amount"""
        if re.match(r'^(\d+)(,(\d{2,3},)*\d{3})?(\.\d{2})?$', candidate): return True
        return False

    def get_single_val_cols(self, df):
        """Return column names that contain either of date or amount"""
        cols = []
        for col in df.columns:
            if all(df[col].apply(lambda elem: not elem or self.is_date(elem) or self.is_amount(elem))):
                cols.append(col)
        return cols

    @staticmethod
    def find_starting_rows(df, single_val_cols:List[int]):
        starts = set()
        for col in single_val_cols:
            starts = starts.union(df.index[df[col].astype(bool)])
        # Add an extra index for merging trailing line if any
        starts.add(max(df.index)+1)
        starts = sorted(list(starts))
        return starts


@click.command()
@click.argument('path', type=click.Path(exists=True, dir_okay=False, file_okay=True)) # First Arg, path
@click.argument('out_dir', type=click.Path()) # 2nd argument output directory
def extract_tables(path, out_dir):
    base_name = os.path.splitext(os.path.basename(path))[0]
    os.makedirs(os.path.join(out_dir, base_name), exist_ok=True)
    extractor = TableExtractor(path)
    for i, df in enumerate(extractor.tables):
        df = extractor.process_df(df)
        df.to_excel(os.path.join(out_dir, base_name, f'table_{i}.xlsx'))


if __name__ == '__main__':
    extract_tables()
