from matplotlib import rcParams,font_manager
import pprint

pp = pprint.PrettyPrinter(indent=4)

'''
fonts-noto-cjk
fc-list :lang=zh
fc-list --format=%{file}\\n

'''
pp.pprint(font_manager.findSystemFonts(fontpaths=None, fontext='ttf'))
pp.pprint(sorted(font_manager.get_font_names()))