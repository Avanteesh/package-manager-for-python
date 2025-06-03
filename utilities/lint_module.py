import ast
import os
import re
import warnings
import colorama as col
from utilities.info import Config
from collections import deque

class ExtendedNodeVisitor(ast.NodeVisitor):
    def __init__(self, ignore_warning: bool):
        self.ignore_warning = ignore_warning
        self.globals = set()

    def visit(self, node: ast.AST):
        if isinstance(node, ast.FunctionDef):
            self.visit_FunctionDef(node)
        elif isinstance(node, ast.Call):
            self.visit_Call(node)
        elif isinstance(node, ast.ClassDef):
            self.visit_ClassDef(node)
        elif isinstance(node, ast.ImportFrom):
            self.visit_ImportFrom(node)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        for arg_types in node.args.defaults:
            if isinstance(arg_types, ast.List) == True and self.ignore_warning == False:
                warnings.warn(f"{col.Fore.RED}Warning at Line:{node.lineno}{col.Fore.WHITE} mutable default arguments are not allowed!")
        for child_nodes in node.body:
            if isinstance(child_nodes, ast.Import) and self.ignore_warning == False:
                warnings.warn(f"{col.Fore.RED}Warning at Line:{col.Fore.WHITE} {child_nodes.lineno} Don't import locally inside a function!")
            elif isinstance(child_nodes, ast.FunctionDef):
                self.visit_FunctionDef(child_nodes)
    
    def visit_Call(self, node):
        if node.func.id == "eval" and self.ignore_warning == False:
            warnings.warn(f"{col.Fore.RED}Warning at Line:{col.Fore.WHITE} {node.lineno} Do not use the 'eval'function, its prone to string injection attacks!")

    def visit_ClassDef(self, node):
        if (not (ord(node.name[0]) >= 65 and ord(node.name[0]) <= 91)) and self.ignore_warning == False:
            warnings.warn(f"{col.Fore.RED}Warning: {col.Fore.WHITE} class names must be capital!")

    def visit_ImportFrom(self, node):
        # prevent wild card imports to avoid namespace collision!
        if node.names[0].name == "*" and self.ignore_warning == False:
            warnings.warn(f"{col.Fore.RED}Warning: {col.Fore.WHITE} wildcard import can lead to namespace pollution, instead import specific functions only!")

def analyzePySourceFiles(ignore_warning: bool=False):
    current = os.path.split(os.getcwd())[-1]
    if not os.path.exists(Config.DEPS_FILE.value):
        print(f"{col.Fore.RED}ERROR:{col.Fore.RED} package.json file not found, initialize your project first!")
        os._exit(1)
    queue = deque()
    queue.append(".")
    while len(queue) != 0:
        first = queue.popleft()
        for content in os.listdir(first):
            _file = os.path.join(first, content)
            if os.path.isfile(_file) == True and re.search(r"\.py", _file) is not None:
                tree = ""
                with open(_file, "r") as f1:
                    tree = ast.parse(f1.read())
                node_vistor = ExtendedNodeVisitor(ignore_warning)
                node_vistor.visit(tree)
            elif os.path.isdir(content):
                if first == "." and content == Config.DEPS_FOLDER.value:pass
                else:queue.append(os.path.join(first, content))




