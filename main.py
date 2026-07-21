import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.db_helper import init_db


def main():
    parser = argparse.ArgumentParser(description='招聘市场数据分析系统')
    parser.add_argument('command', choices=['init', 'crawl', 'analyze', 'dashboard'],
                        help='执行命令: init(初始化数据库), crawl(爬取数据), analyze(数据分析), dashboard(可视化看板)')
    parser.add_argument('--source', choices=['boss', 'lagou', 'kanzhun', 'all'], default='all',
                        help='数据源选择 (默认: all)')
    parser.add_argument('--keyword', type=str, default='数据分析师',
                        help='搜索关键词 (默认: 数据分析师)')
    parser.add_argument('--city', type=str, default='北京',
                        help='城市 (默认: 北京)')
    parser.add_argument('--pages', type=int, default=10,
                        help='爬取页数 (默认: 10)')

    args = parser.parse_args()

    if args.command == 'init':
        print('=' * 50)
        print('初始化招聘市场数据分析系统')
        print('=' * 50)
        init_db()
        print('\n系统初始化完成！')
        print('  数据库文件: data/jobs.db')
        print('  下一步: 运行 python main.py crawl 开始爬取数据')

    elif args.command == 'crawl':
        print(f'开始爬取数据 - 来源: {args.source}, 关键词: {args.keyword}, 城市: {args.city}')
        print('提示: 爬虫功能正在开发中...')

    elif args.command == 'analyze':
        print('数据分析模块开发中...')

    elif args.command == 'dashboard':
        print('可视化看板开发中...')


if __name__ == '__main__':
    main()
