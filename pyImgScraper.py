from urlparse import urljoin
import argparse
import urllib
import lxml.html
import os
import sys
import threading
import requests
import Queue
import timeit

def main_fn():
	script,url = sys.argv
	if not url.startswith('http'):
		url = "http://"+url
	PyImgScraper(url).start()

class ThreadPool():
	def __init__(self,threadcount):
		self.jobs = Queue.Queue(threadcount)
		for _ in range(threadcount):
			DownloadImg(self.jobs)
	def add_job(self,*args):
		self.jobs.put(args)
	def jobs_complete(self):
		self.jobs.join()

class DownloadImg (threading.Thread):
	def __init__(self,jobs):
		threading.Thread.__init__(self)
		self.jobs = jobs
		self.daemon = True
		self.start()
	def run(self):
		args = self.jobs.get()
		func,image_link,file_loc = args
		func(image_link,file_loc)
		self.jobs.task_done()

class PyImgScraper(object):
	"""main scraper class"""
	def __init__(self,url):
		self.url = url
		self.links = []
		self.directory = "images"+"-"+url.split('/')[2]
		self.img_count = 0
		self.success_count = 0
		self.failure_count = 0
		self.downloaded_links = []
		self.failed_links = []
		self.img_fmts = ["jpg", "png", "gif", "svg", "jpeg"]

	def start(self):
		self.imgscraper()

	def generate_scrap_report(self):
		with open(self.directory+"/scrap-report.txt",'wb') as f:
			f.write("###-PyImgScraper-###\n\n"+"url : %s\nNumber of images downloaded : %s\nFailed downloads : %s\nTime elapsed : %sseconds\n"
				%(self.url,self.success_count,self.failure_count,self.elapsed))
			f.write("\n\n---Successful downloads---\n\n")
			for link in self.downloaded_links:
				f.write("%s\n" %link)
			f.write("\n\n---Failed downloads---\n\n")
			for link in self.failed_links:
				f.write("%s\n" %link)

	def gethtmlsource(self):
	#	print "\nGetting html source code..."
		self.html = requests.get(self.url).text
		self.dom =  lxml.html.fromstring(self.html)
		#print "\nImages found = %d\n"%self.img_count

	def acquire_links(self):
		self.imglinks = self.dom.xpath('//img/@src')
		self.img_count = len(self.imglinks)
		for link in self.imglinks:
			self.links.append(urljoin(self.url,link))


	def download_img(self,image_link,file_loc):
		try:
			image_request = requests.get(image_link, stream=True)
			if image_request.status_code == 200:
				with open(file_loc,'wb') as f:
					f.write(image_request.content)
				self.success_count += 1
				self.downloaded_links.append(image_link)
			else:
				self.failure_count += 1
				self.failed_links.append(image_link)
		except:
			self.failure_count += 1
			self.failed_links.append(image_link)

	def imgscraper(self):
		if not os.path.exists(self.directory):
			os.makedirs(self.directory)

		self.gethtmlsource()

		print "\nProcessing links..."

		self.acquire_links()

		self.start_time = timeit.default_timer()
		pool = ThreadPool(self.img_count)
		for link in self.links:		
			file_name = link.split('/')[len(link.split('/'))-1]
			file_loc = self.directory+"/"+file_name
			pool.add_job(self.download_img,link,file_loc)
		while(True):
			self.percentage = (self.success_count+self.failure_count)/float(self.img_count)*100
			sys.stdout.write("\rDownload progress:{0:.0f}%".format(self.percentage))
			sys.stdout.flush()
			if self.success_count+self.failure_count -  self.img_count == 0:
				break
		pool.jobs_complete()
		sys.stdout.write("\rDownload progress:{0:.0f}%\n".format(100))
		sys.stdout.flush()
		self.elapsed = timeit.default_timer() - self.start_time
		print "\nGenerating scrap report..."

		self.generate_scrap_report()

		print "\nProcess complete!"
		print "Successful downloads = %s"%self.success_count
		print "Failed downloads = %s"%self.failure_count
		print "Time Elapsed = %ds"%self.elapsed

main_fn()