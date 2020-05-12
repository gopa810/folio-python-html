
import html_scan as hs






with open('data/gfolio/BOOKS/SSD/ch08_sadhana1.html','rt') as ifi:
    parser = hs.HtmlScanResult()
    a = ifi.read()
    parser.feed(a)
    print(parser.Lines)
