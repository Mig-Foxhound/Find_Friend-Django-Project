import urllib2
import re
import collections


class popCrawl(object):
  def __init__(self):
    pass
  def gethtml(self, keyword):  
      url = 'https://www.google.co.il/search?q=' + keyword
      user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36'
      headers = { 'User-Agent' : user_agent }
      req = urllib2.Request(url, None, headers)
      html = urllib2.urlopen(req).read()
      return html


  def pophtml(self, raw_html):
    popdata = re.findall(r'(\[\d+,\[\d+,)((\d+,)*)(\d+\])', raw_html)
    return popdata

  def engine(self, keyword):
    d = collections.defaultdict(list)
    for tm in range(0, 24):
      d[tm] = []

    htmldata = self.gethtml(keyword)
    popdata = self.pophtml(htmldata)
  
    offset = 0
    for pdata in popdata:
      for idx, tm_pt in enumerate(str(pdata).split(",")):
        datapt = unicode(tm_pt.strip("'([]) "),'utf-8')
        if idx==0 and datapt.isnumeric():
          start_time = int(datapt)
          offset = 0

        elif idx!=0 and datapt.isnumeric():
          d[(start_time+offset)%24].append(int(datapt))
          offset += 1
    ret_d = {}
    for k, v in d.items():
      if v:
        ret_d[k] = sum(v)//len(v)
      else:
        ret_d[k] = 0
    return ret_d

# if __name__ == '__main__':
#   mycrawl = popCrawl()
#   print("Grainger:", mycrawl.engine("Grainger%20Library"))
#   print("UGL:", mycrawl.engine("UGL"))
#   print("sakanaya", mycrawl.engine("sakanaya"))
#   print("miga", mycrawl.engine("miga"))
