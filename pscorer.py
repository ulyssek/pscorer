
from PyPDF2 import PdfReader

from PyPDF2.errors import PdfReadError

import re


import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns



class PScorer():

	##########################################################################################
	##########################################################################################
	#### Init section
	####

	def __init__(self,default_pattern=None,files_path='./'):
		#####################################################
		## default_pattern : pattern to be used in p-values search 
		
		if default_pattern is None:
			self.default_pattern = '[P|p][ ]*[=|<]*[ ]*[0-9]?[.][0-9]+'
		else:
			self.default_pattern = default_pattern

		self.files_path = files_path

	##########################################################################################
	##########################################################################################
	#### Core Functions
	####

	def distrib(self,pdf_file,bins=None,significant=True,title=None,search_pattern=None,convert_function=None):
		#####################################################
		## Main function to call, will gather p_values, clean them and plot the distrib 

		if type(pdf_file) == str:
			p_values = self.get_p_values(pdf_file,search_pattern=search_pattern,convert_function=convert_function)
		else:
			p_values = []
			for file in pdf_file:
				p_values.extend(self.get_p_values(file,search_pattern=search_pattern,convert_function=convert_function))

		return self.plot_distrib(p_values,bins,significant,title=title)

	def get_p_values(self,pdf_file,talky=False,v_talky=False,search_pattern=None,utf8=True,convert_function=None):
		#####################################################
		## pdf_file : pdf file to be scored
		## talky : will display information 
		## v_talky : (very_talky) will dispay a lot of information
		## search_pattern : pattern to be used in p-values search
		
		raw_p_values = self._get_raw_p_values(pdf_file,talky,v_talky,search_pattern,utf8=utf8)
		p_values = list(map(lambda x:self._get_p_values_from_raw_p_value(x,convert_function=convert_function),raw_p_values))

		return p_values

	##########################################################################################
	##########################################################################################
	#### P_values Functions
	####

	def _get_raw_p_values(self,pdf_file,talky=False,v_talky=False,search_pattern=None,utf8=True):
		#####################################################
		## will find the raw p_values, as writen in the pdf file

		if search_pattern is None:
			search_pattern = self.default_pattern

		with open(self.files_path+pdf_file, 'rb') as file:
			pdf = PdfReader(file)
			try:
				number_of_pages = len(pdf.pages)
			except PdfReadError:
				print("Could not read pdf, sry bro")
				return []

			p_values = [] #List of p-values to be returned

			for i in range(number_of_pages):
				try:
					page_content = pdf.pages[i].extract_text()
				except TypeError:
					print("Could not read pdf, sry bro")
					return []
				if v_talky:
					if utf8:
						print(page_content.encode("utf-8"))
					else:
						print(page_content)
				result = re.findall(search_pattern, page_content)
				if talky:
				    print("Page "+str(i+1))
				    print(result)
				p_values.extend(result)
		
		return p_values


	def _get_p_values_from_raw_p_value(self,p_value,convert_function=None):
		#####################################################
		## removing all unwanted characters 

		d = p_value
		d = d.split("]")[0]
		d = d.split('p')[-1]
		d = d.split('P')[-1]
		d = d.split(' ')[-1]
		d = d.split('=')[-1]
		d = d.split('<')
		if len(d) == 1:
			if convert_function is None:
				return self._convert(d[0])
			else:
				return convert_function(self,d[0])
				"""
				e = d[0].split('×')
				if len(e) == 1:
					convert_d = self._convert(d[0])
					return float(convert_d)
				else:
					a = e[0]
					b = e[1].split('\n')[-1]
					return float(a)*10**(-float(b))
				"""
		else:
			convert_d = self._convert(d[1])
			if convert_d == d:
				print("P-value not recognized : " + p_value)
				return float(convert_d)
			else:
				return float(convert_d)


	def _convert(self,p_value):
		if p_value in ('0.05','.05'):
			return np.random.rand()*2/50+.01
		elif p_value in ('0.01', '.01'):
			return np.random.rand()*9/1000+.001
		elif p_value in ('0.001', '.001'):
			return np.random.rand()/10000
		return float(p_value)


	def remove_non_significant(self,p_values):
		#####################################################
		## remove all p_values greater than .05 

		results = []
		for p_value in p_values:
			if p_value <= .05:
				results.append(p_value)
		return results

	##########################################################################################
	##########################################################################################
	#### Drawing functions 
	####

	def plot_distrib(self,p_values,bins=None,significant=True,title=None):
		#####################################################
		## Will plot the distribution of p_values
		## p_values : p_values to be plotted
		## bins : bins for the distribution, default value if None
		## significant : will remove non significant p_values if True
		## title : title of the graph, will put the bin size if None 

		if not significant:
			bin_size = .05
			xmax = 1
		else:
			bin_size = .002
			xmax = .05
		if bins is None:
			bins = np.arange(0,xmax+bin_size,bin_size)
		else:
			bin_size = bins[1]-bins[0]
		if significant:
			p_values = self.remove_non_significant(p_values)
		if len(p_values) < 2:
			print("Not enough p_values found")
			return
		sns.distplot(p_values,bins=bins)
		if title is None:
			title = "p-values distribution (bin size : " + str(bin_size) + ")"
		plt.title(title)
		plt.xlim(0,xmax)
		plt.show()
		return p_values

