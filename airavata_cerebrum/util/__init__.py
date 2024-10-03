
#

def class_qual_name(src_class):
    return  ".".join([src_class.__module__, src_class.__name__])
