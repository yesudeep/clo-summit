import base64
import logging
from google.appengine.api import memcache
from jinja2 import FileSystemLoader

try:
    mydata
except NameError:
    logging.error("mydata is undefined")
    mydata = {}

def get_data_by_name(name):
    if base64.b64encode(name) in mydata:
        return mydata[base64.b64encode(name)]
    return None

class PythonLoader(FileSystemLoader):
    """A Jinja2 loader that loads pre-compiled templates."""
    def load(self, environment, name, globals=None):
        """Loads a Python code template."""
        if globals is None:
            globals = {}
        #try for a variable cache
        code = get_data_by_name(name)
        if code is not None:
            logging.info("ultrafast memcache")
        else:
            logging.info("slow memcache")
            code = memcache.get(name)
            if code is None:
                logging.info("oops no memcache!!")
                source, filename, uptodate = self.get_source(environment, name)
                template = file(filename).read().decode('ascii').decode('utf-8')
                code = environment.compile(template, raw=True)
                memcache.set(name,code)
                logging.info(name)
            else:
                logging.info("yeh memcache")
            code = compile(code, name, 'exec')
            mydata[base64.b64encode(name)] = code
        return environment.template_class.from_code(environment, code, globals)

