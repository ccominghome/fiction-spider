import hashlib


# 为每一个chapter生成一个唯一的id
def generate_unique_fingerprint_for_unique_chapter_id(item1, item2):
    fp = hashlib.sha1()
    fp.update(item1.encode("utf8"))
    fp.update(item2.encode("utf8"))
    return fp.hexdigest()
