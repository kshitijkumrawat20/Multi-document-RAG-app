import os
class DocumentOperation:
    @staticmethod
    def get_file_type_by_extension(filename):
        _, extension = os.path.splitext(filename)
        extension = extension.lower()
        if extension == ".txt":
            return "text"
        elif extension == ".pdf":
            return "pdf"
        elif extension in [".doc", ".docx"]:
            return "word"
        else:
            return "unknown"