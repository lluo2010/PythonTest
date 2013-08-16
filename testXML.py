#coding=utf-8
import sys
#from xml.etree.ElementTree import Element, SubElement, Comment,XML
from xml.etree.ElementTree import Element, SubElement, ElementTree,Comment
from xml.etree.ElementTree import tostring
from xml.dom import minidom

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = tostring(elem,'utf-8') #ElementTree.tostring()
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def createXml():
    top = Element("top")
    comment = Comment("this is a xml test")
    top.append(comment)
    info = SubElement(top,"info") # add sub element
    for i in range(4):
        name = "name %d"%i
        # set attribute, the third parameter is dictionary
        people1 = SubElement(info,"people",
                             {"age":str(i),"name":name}
                             )
        people1.text = "people%d" %(i) #set text
        
    peopleElementList = [Element("people",{"age":str(i),"name":"name"+str(i)}) for i in range(5,9)]
    for (index,ele) in enumerate(peopleElementList):
        ele.text = "people%d" %(index+5)
    #use extend to add element list
    info.extend(peopleElementList)
    #peopleEleList2 = XML('''<people age="0" name="name 0">people0</people><people age="1" name="name 1">people1</people><people age="2" name="name 2">people2</people>''')
    #info.extend(peopleEleList2)
    
    print prettify(top)
    
    #Serializing XML to a Stream
    ElementTree(top).write(sys.stdout)

    
    #XML to a 
    ElementTree(top).write(sys.stdout)
def parseXml():
    pass
if __name__=="__main__":
    createXml()
    pass

