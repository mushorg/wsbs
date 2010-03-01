import xml.dom.minidom

class ReportParser():

    def get_text(self, node_list):
        node_text = ""
        for node in node_list:
            if node.nodeType == node.TEXT_NODE:
                node_text += node.data
        return node_text
    
    def handle_report(self, xml_file):
        self.CnC_IP = ""
        self.CnC_PORT = 0
        self.CnC_USER = ""
        self.CnC_NICK = ""
        self.CnC_CHAN = []
        try:
            report = xml.dom.minidom.parse(xml_file)
        except:
            return ["","","","",""]
        self.handle_report_title(report.getElementsByTagName("file_name")[0])
        function_calls = report.getElementsByTagName("function_call")
        self.handle_functions(function_calls)
        return self.CnC_IP, self.CnC_PORT, self.CnC_CHAN, self.CnC_NICK, self.CnC_USER

    def handle_report_title(self, title):
        # expects: <title>Demo slideshow</title>
        #print "Report for: %s" % self.get_text(title.childNodes)
        pass
        
    def handle_functions(self, function_calls):
        for function in function_calls:
            self.handle_function(function)
            
    def handle_function(self, function):
        self.function_name = self.handle_function_name(function.getElementsByTagName("name")[0])
        self.function_parameter = self.handle_function_parameter(function.getElementsByTagName("parameter")[0])
        if self.function_name == "fsockopen":
            self.CnC_IP = self.function_parameter.partition("host=")[2].partition(",")[0]
            self.CnC_PORT = int(self.function_parameter.rpartition("port=")[2].partition(",")[0])
        if "string=\"USER" in self.function_parameter:
            self.CnC_USER = self.function_parameter.partition("USER")[2].partition("\"")[0].strip()
        if "string=\"NICK" in self.function_parameter:
            self.CnC_NICK = self.function_parameter.partition("NICK")[2].partition("\"")[0].strip()
        if "string=\"JOIN" in self.function_parameter:
            self.CnC_CHAN.append(self.function_parameter.partition("JOIN")[2].partition("\"")[0].strip())
            
    def handle_function_name(self, function_name):
        return self.get_text(function_name.childNodes)
    
    def handle_function_parameter(self, function_parameter):
        return self.get_text(function_parameter.childNodes).replace("\n","")