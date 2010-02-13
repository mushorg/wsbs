import xml.dom.minidom

output = """\
<report>
<title>PHP bot</title>
    <function_call>
        <name>fsockopen</name>
        <parameter>irc.freenode.org:6667</parameter>
    </function_call>
    <function_call>
        <name>fwrite</name>
        <parameter>JOIN #party\n</parameter>
    </function_call>
</report>
"""


class ReportParser():
    
    def get_text(self, node_list):
        node_text = ""
        for node in node_list:
            if node.nodeType == node.TEXT_NODE:
                node_text += node.data
        return node_text
    
    def handle_report(self, xml_file):
        report = xml.dom.minidom.parseString(xml_file)
        self.handle_report_title(report.getElementsByTagName("title")[0])
        function_calls = report.getElementsByTagName("function_call")
        self.handle_functions(function_calls)
    
    def handle_report_title(self, title):
        # expects: <title>Demo slideshow</title>
        print "Report for: %s" % self.get_text(title.childNodes)
        print "="*4
        
    def handle_functions(self, function_calls):
        for function in function_calls:
            self.handle_function(function)
            print "="*4
            
    def handle_function(self, function):
        self.handle_function_name(function.getElementsByTagName("name")[0])
        self.handle_function_parameter(function.getElementsByTagName("parameter")[0])
    
    def handle_function_name(self, function_name):
        print "function name: %s" % self.get_text(function_name.childNodes)
    
    def handle_function_parameter(self, function_parameter):
        print "function parameter: %s" % self.get_text(function_parameter.childNodes).replace("\n","")

xml_parser = ReportParser()
xml_parser.handle_report(output)