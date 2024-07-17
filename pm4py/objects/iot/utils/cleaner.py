import os

"""
    Rewrites log, correcting the data, the output written to the modified_path file
"""
def rewrite(path, modified_path):
    if path == modified_path:
        raise Exception("Can't rewrite the same file path={}".format(path))
    
    fin = open(path, "rt")
    fout = open(modified_path, "wt")

    attribute_string_to_list = ['stream:point', 'stream:meta', 'meta', 'value', 'stream:source', 'stream:multipoint']
    for i, line in enumerate(fin):
        content = line.split("\"")
        line = line.replace('date key="cpee:activity_uuid"', 'string key="cpee:activity_uuid"')
        line = line.replace('date key="cpee:instance"', 'string key="cpee:instance"')
        line = line.replace('value=""', 'value="__NOTSPECIFIED__"')
        line = line.replace('value="__INVALID__"', 'value="__NOTSPECIFIED__"')
        
        if len(content) > 0:
            if len(content) == 3 and (content[1] in attribute_string_to_list) and content[0].lstrip().startswith('<string'):
                line = line.replace('<string', '<list')
            if content[0].lstrip().startswith('</string>'):
                line = line.replace('</string>', '</list>')

        fout.write(line)

    fin.close()
    fout.close()

def remove_modified(modified_path):
    if not os.path.exists(modified_path):
        raise Exception('File does not exist, modified_path={}'.format(modified_path))
    if not os.path.basename(modified_path).startswith('modified_'):
        raise Exception('File does not start with modified_ prefix, modified_path={}'.format(modified_path))
    os.remove(modified_path)
