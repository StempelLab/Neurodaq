# Get browser instance
global browser

def set_browser(b):
    # Called by mainWindow.py to set global browser
    global browser
    browser = b
        
        
class ToolSelector():
    """ Class for selecting the appropriate function
    when the Analysis action is called.
    """
    
    def __init__(self):
        self.tools = []
    
    def add_tool(self, toolName, toolFunc):
        self.tools.append([toolName, toolFunc])
        
    def tool_select(self, browser, selectedTool):
        for tool in self.tools:
            if selectedTool==tool[0]: tool[1](browser)

                  
