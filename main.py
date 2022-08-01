import argparse
import ast
from pathlib import Path

from tomlkit import string

def get_pydantic_model_names(myAst: ast.AST) -> list[str]:
    module_names = []
    for node in ast.walk(myAst):
        if type(node) not in [ast.Import, ast.ImportFrom]:
            continue    
        for e in node.names:
            if isinstance(e, ast.alias) and e.name == 'BaseModel':
                name = getattr(e, 'asname') or e.name
                module_names.append(name) 
            elif isinstance(e, ast.alias) and e.name == 'pydantic':
                name = getattr(e, 'asname') or e.name
                module_names.append(name + '.BaseModel')
    return module_names

def get_pydantic_classes(myAst: ast.AST) -> dict[str, int]:
    modules = get_pydantic_model_names(myAst)
    classes = dict()
    for node in ast.walk(myAst):
        if type(node) != ast.ClassDef:
            continue
        for i in node.bases:
            current_classes = modules + list(classes.keys())
            if i == [ast.Attribute, ast.Name]:
                continue
            name = getattr(i, 'id', None)
            if not name:
                name = f"{i.value.id}.{i.attr}"  
            if name in current_classes:
                classes[node.name] = node
            
    return classes

def reorder_pydantic_fields(myAst: ast.AST):
    classes = get_pydantic_classes(myAst)
    for obj in classes.values():
        elements = obj.body
        obj.body = []
        
        required, optional = [], []
        for el in elements: 
            if type(el.annotation) == ast.Subscript:
                if el.annotation.value.id == 'Optional':
                    optional.append(el)
            else:
                required.append(el)

        required = sorted(required, key=lambda x: x.target.id)
        optional = sorted(optional, key=lambda x: x.target.id)
        obj.body = required + optional 
    return myAst

if '__main__' == __name__:
    import sys
    path = sys.argv[1]
    if not path:
        raise "Dupa error"

    file = Path(path)
    code = file.read_text()
    tree = ast.parse(code)
    reordered_ast = reorder_pydantic_fields(tree)

    new_file_path = Path(str(file).replace(file.suffix, "_reordered" + file.suffix)) 
    with open(new_file_path, 'w') as f:
        f.write(ast.unparse(reordered_ast))