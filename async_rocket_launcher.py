#!/usr/bin/env python

# builtin module
from datetime import datetime
import sys

# pip install module
import requests
from thespian.actors import *
from bs4 import BeautifulSoup


URL_TPL = "http://comic.naver.com/webtoon/list.nhn?titleId=20853&weekday=tue&page={}"

def get_html(url):    
    resp = requests.get(url)
    response = Response(resp)
    return response

def parse_html(html):
    """
    입력받은 마음의 소리 웹툰 페이지 html에서 마음의소리의 회차, 제목 url을 추출하여
    tuple로 만들고, 리스트에 갯수대로 저장하여 반환한다
    :param html: string
    :return: 마음의 소리 정보가 담긴 리스트
    """
    webtoon_list = list()
    soup = BeautifulSoup(html, 'html.parser')
    webtoon_area = soup.find("table",
            {"class": "viewList"}
            ).find_all("td", {"class":"title"})
    for webtoon_index in webtoon_area:
        info_soup = webtoon_index.find("a")
        _url = info_soup["href"]
        _text = info_soup.text.split(".")
        _title  = ""
        _num = _text[0]
        if len(_text) > 1:
            _title = _text[1]
            
        webtoon_list.append((_num, _title, _url, ))

    return ParseResult(items = webtoon_list)


class Response(object):
    def __init__(self, result):
        self.text = result.text
        self.code = result.status_code
    def __str__(self):
        return "{}".format(self.code)

class ParseResult(object):
    def __init__(self, items = []):
        self.items = items

    def __repr__(self):
        return "test"

class Collector(Actor):
    def receiveMessage(self, url, sender):
        if isinstance(url, str):
            resp = get_html(url)
            parser = self.createActor(Parser)            
            #resp.sendTo = [printer, sender]
            self.send(parser, resp)


class Parser(Actor):
    def receiveMessage(self, response, sender):
        if isinstance(response, Response):
            parse_result = parse_html(response.text)
            printer_manager = self.createActor(PrinterManager)
            #nextTo = response.sendTo.pop(0)
            #print("nextTo: {}".format(nextTo))
            self.send(printer_manager, parse_result)


class PrinterManager(Actor):
    def receiveMessage(self, result, sender):
        if isinstance(result, ParseResult):
            printer = self.createActor(Printer)
            for item in result.items:
                self.send(printer, item)


class Printer(Actor):
    def receiveMessage(self, webtoon_infos, sender):
        if isinstance(webtoon_infos, tuple):
            idx = 0
            print("index: {}, list_num: {}, info: {}".format(idx, webtoon_infos[0], webtoon_infos))


# class Hello(Actor):
#     def receiveMessage(self, message, sender):
#         if message == 'hi':
#             greeting = Greeting('Hello')
#             world = self.createActor(World)
#             punct = self.createActor(Punctuate)
#             greeting.sendTo = [punct, sender]
#             self.send(world, greeting)

# class World(Actor):
#     def receiveMessage(self, message, sender):
#         if isinstance(message, Greeting):
#             message.message = message.message + ", World"
#             nextTo = message.sendTo.pop(0)
#             self.send(nextTo, message)

# class Punctuate(Actor):
#     def receiveMessage(self, message, sender):
#         if isinstance(message, Greeting):
#             message.message = message.message + "!"
#             nextTo = message.sendTo.pop(0)
#             self.send(nextTo, message)

if __name__ == "__main__":    
    # hello = ActorSystem().createActor(Hello)
    # print(ActorSystem().ask(hello, 'hi', 0.2))
    # print(ActorSystem().ask(hello, 'hi', 0.2))
    # ActorSystem().tell(hello, ActorExitRequest())
    # print(ActorSystem().ask(hello, 'hi', 0.2))
    collector = ActorSystem().createActor(Collector)
    print(ActorSystem().ask(collector, URL_TPL.format(1)))
    print(ActorSystem().ask(collector, URL_TPL.format(2)))
    ActorSystem().tell(collector, ActorExitRequest())
    print(ActorSystem().ask(collector, URL_TPL.format(3)))

