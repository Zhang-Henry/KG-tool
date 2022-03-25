class wsparam_save(object):
    def __init__(self):
        self.wsparam = None
        self.sentence = []
        self.mie_sentence = []
        self.dialogue = []

    def getparam(self):
        return self.wsparam

    def modify(self, modVal):
        self.wsparam = modVal

    def addSentence(self, sent):
        speakers = {"0": "患者", "1": "医生"}
        types = {"0": "info", "1": " "}
        sent = sent.replace("，", "")
        sent = sent.replace("。", "")
        sent = sent.replace("？", "")
        if sent != "":
            length = len(self.sentence)
            speaker = speakers[str(length % 2)]
            type = types[str(length % 2)]
            self.sentence.append(
                {"speaker": speaker, "sent": sent, "type": type})
            self.mie_sentence.append(speaker+":"+sent)

    def getSentence(self):
        return self.sentence

    def clearSentence(self):
        self.sentence = []
        self.mie_sentence = []

    def addDialogue(self):
        if self.mie_sentence != []:
            self.dialogue.append(self.mie_sentence)

    def getDialogue(self):
        return self.dialogue

    def clearDialogue(self):
        self.dialogue = []


wsparam_all = wsparam_save()
