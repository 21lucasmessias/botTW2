from setuptools import setup

setup(
   name             = 'bot-tw2',
   version          = '1.0.0',
   description      = 'A bot for Tribal Wars 2',
   packages         = ['rash_bot_tw2'],
   install_requires = [
      'asyncio~=3.4.3',
      'websockets~=8.1',
   ],
)
