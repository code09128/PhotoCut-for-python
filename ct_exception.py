class CT_Exception(Exception):
    def __init__(self, msg, cutting_imgs):
        self.message=msg
        self.cutting_imgs = cutting_imgs