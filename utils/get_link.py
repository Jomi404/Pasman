from aiogram.utils.markdown import hlink


def getHyperLink(url: str, title: str):
    link = url
    title = title
    hyperlink = hlink(title, link)
    return hyperlink