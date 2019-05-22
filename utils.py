def safe_remove(parent, name):
    if name in parent.children_names:
        parent.remove(name)
