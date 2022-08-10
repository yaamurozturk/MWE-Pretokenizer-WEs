#%%
from typing import Iterator,Callable, Any, Union, Optional
from conllu import TokenList, parse_incr, TokenTree
import pandas as pd
from pandas import DataFrame
from itertools import chain, takewhile, count
import re

class Conllu_df_parser:
	def __init__(
		self, 
		src : Union[str, list[TokenList]],
		preprocessing : Optional[list[Callable[[TokenList], TokenList]]] = None,
		postprocessing : Optional[list[Callable[[DataFrame], DataFrame]]] = None
	):
		'''Setup a parser which takes a .conll / .conllu / .cupt or and list of 
		TokenList and outputs a DataFrame where each feature is a column,
		each word a row, and TokenTree of each word is a the ...

		Parameters
		----------
		src : str | list[TokenList]
			either the path to the .conll / .conllu / .cupt file or list of Tokenlist.
		preprocessing : list[Callable[[TokenList], TokenList]] | None, optional
			list of functions (TokenList) -> TokenList to be executed before the
			Dataframe et TokenTree are generated, by default None
		postprocessing : list[Callable[[DataFrame], DataFrame]] | None, optional
			list of functions (DataFrame) -> DataFrame to be executed after the 
			DataFrame and the TokenTree are generated 
			(usefull when working with batches), by default None

		Raises
		------
		TypeError
			if src's type is incorrect
		'''
		if type(src) == str:
			file = open(src, 'r', encoding="utf-8")
			self.parser_TL = parse_incr(file)
		elif type(src) == list:
			self.parser_TL = src
		else :
			raise TypeError
			
		
		self._has_ended = False
		self._counter = 0
		self._preprocessing = preprocessing or [] # same as: preprocessing if preprocessing != None else []
		self._postprocessing = postprocessing or [] # it's magic
	def read_next_n(self, n : int = 0) -> Iterator[TokenList]:
		'''
		Iterates over the next n Tokenlists and apply the preprocessing
		'''
		for i, tl in enumerate(self.parser_TL):
			for f in self._preprocessing:
				tl = f(tl)
			yield tl
			if i >= n-1 and n != 0:
				return
		self._has_ended = True
	def get_df_per_batch(self, batch_size : int) -> Iterator[DataFrame]:
		def tt_to_tts(tree : TokenTree) -> list[TokenTree]:
			return [tree] + list(chain.from_iterable(tt_to_tts(child) for child in tree.children))

		def tl_to_ordered_tts(sentence : TokenList):
			return sorted(tt_to_tts(sentence.to_tree()), key = lambda x: x.token['id'])

		while not self._has_ended:
			df = DataFrame.from_dict(
				{
					(self._counter + m, token['id']): { 
						**token, 
						'TT' : next(tt) if type(token['id']) == int else None
					}
					for m, (tl, tt) in enumerate(map(
						lambda x : (
							x, 
							filter(lambda tt: tt.token['id'] != 0, tl_to_ordered_tts(x))
						),
						self.read_next_n(batch_size)
					))
					for token in tl
				},
				orient='index'
			)
			df.index = df.index.rename(['sentence_id', 'token_id'])
			for f in self._postprocessing:
				df = f(df)
			yield df
			self._counter += batch_size
	def get_df(self) -> DataFrame:
		return next(self.get_df_per_batch(0))

	def get_df_no_tt_per_batch(self, batch_size):
		df =  DataFrame.from_dict(
			{
				(self._counter + m, token['id']): {**token}
				for m, tl in enumerate(self.read_next_n(batch_size))
				for token in tl
			},
				orient='index'
		)
		df.index = df.index.rename(['sentence_id', 'token_id'])
		for f in self._postprocessing:
			df = f(df)
		yield df
		self._counter += batch_size
	def get_df_no_tt(self) -> DataFrame:
		return next(self.get_df_no_tt_per_batch(0))
	

def atomize(tl : TokenList) -> TokenList:
	'''
	atomize the column 'feats'
	'''
	for token in tl:
		token['feats'] = token['feats'] or {} # magic
		for k, v in token['feats'].items():
			token[k] = v
		del token['feats']
	return tl

def remove_compound(df : DataFrame) -> DataFrame:
	'''
	removes all rows of the df where 'id' is not an integer
	'''
	return df.loc[df['id'].apply(type) == int]
		

def locmap(df: DataFrame, column: str, func: Callable[[Any], bool]):
	'''function Monkey patched to pd.DataFrame(check on wiki)
	Given a dataframe, a column of said dataframe and a function
	returns the dataframe containing only those rows for which the function is True.
	
	Is kinda to `.loc` what `.applymap` is to `.apply`.
	`.loc` only takes function which can be vectorized. This method "fixes" that.
	'''
	return df.loc[lambda x: x[column].apply(func)]
DataFrame.locmap = locmap


# def get_mwes3(df : DataFrame) -> DataFrame:
# 	'''Returns a dataframe with (sentence_id, token_id, mwe_id) for index,
# 	with only token from MWEs. If a token is part of multiple MWE it is duplicated 
# 	'''
# 	try:
# 		return pd.concat([
# 			e.assign(mwe_id=i)
# 			for _, v in df.groupby(level=0)
# 			for i, e in takewhile(
# 				lambda x: len(x[1]) != 0,
# 				map(
# 					lambda i : (i, locmap(v, 'parseme:mwe', lambda x: re.search(f'(;|^){i}(;|:|$)', x) != None)),
# 					count(1) 
# 				)
# 			)
# 		]).set_index('mwe_id', append=True)
# 	except:
# 		return locmap(df, 'parseme:mwe', lambda x: re.search(f'(;|^){1}(;|:|$)', x) != None).assign(mwe_id=0)

# def get_mwes2(df : DataFrame) -> DataFrame:
# 	'''Returns a dataframe with (sentence_id, token_id, mwe_id) for index,
# 	with only token from MWEs. If a token is part of multiple MWE it is duplicated 
# 	'''
# 	return pd.concat([
# 		e.assign(mwe_id=i)
# 		for _, v in df.groupby(level=0)
# 		for i, e in takewhile(
# 			lambda x: len(x[1]) != 0,
# 			map(
# 				lambda i : (i, locmap(v, 'parseme:mwe', lambda x: re.search(f'(;|^){i}(;|:|$)', x) != None)),
# 				count(1) 
# 			)
# 		)
# 	]).set_index('mwe_id', append=True)

def get_mwes(df : DataFrame) -> DataFrame:
	'''Returns a dataframe with (sentence_id, token_id, mwe_id) for index,
	with only token from MWEs. If a token is part of multiple MWE it is duplicated 
	'''

	try:
		return pd.concat([
			locmap(
				v,
				'parseme:mwe',
				lambda x: re.search(f'(;|^){i}(;|:|$)', x) != None
			).assign(mwe_id=i)
			for _, v in df.groupby(level=0) # groupby sentence
			for i in {
				y
				for x in v['parseme:mwe'].apply(lambda x: re.findall(f'(?:;|^)(\d+)(?:;|:|$)', x))
				for y in x
			}

			# for i, e in takewhile(
			# 	lambda x: len(x[1]) != 0,
			# 	map(
			# 		lambda i : (i, locmap(v, 'parseme:mwe', lambda x: re.search(f'(;|^){i}(;|:|$)', x) != None)),
			# 		count(1) 
			# 	)
			# )
		]).set_index('mwe_id', append=True)
	except:
		return locmap(df, 'parseme:mwe', lambda x: re.search(f'(;|^){1}(;|:|$)', x) != None).assign(mwe_id=0)
# %%
def inline_mwes(x):
	tmp = x.groupby(level=[0, 2]).apply(lambda x : (tuple(sorted(list(x['lemma']))), tuple(x['id']))).apply(lambda x: pd.Series(x))
	return tmp.reset_index('mwe_id', drop=True).reset_index().drop_duplicates().set_index('sentence_id')
