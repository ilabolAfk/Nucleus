# plugins/hello.py
import webbrowser

def register(api):
    @api.action("hh", "Hello от плагина", "fa5s.hand-peace", "демо")
    def hello(_):
        return "плагины работают!"