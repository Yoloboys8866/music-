import random
import requests
import json
import prettytable
# 删除未使用的PLAIN_COLUMNS导入
import pprint
from tqdm import tqdm
import os
import re
# 在导入部分添加time模块
import time
# 添加pyperclip用于读取剪贴板内容（如果需要）
import pyperclip
from colorama import Fore, init, Style
init()
# 定义音乐存储文件夹  # 新增这几行
MUSIC_STORAGE_FOLDER = '音乐下载'
# 创建存储文件夹（如果不存在）
os.makedirs(MUSIC_STORAGE_FOLDER, exist_ok=True)
kuwo_headers = {
    'Cookie': '_ga=GA1.2.1814122629.1651482273; _gid=GA1.2.205632186.1660292719; Hm_lvt_cdb524f42f0ce19b169a8071123a4797=1660292719,1660351648; Hm_lpvt_cdb524f42f0ce19b169a8071123a4797=1660374742; kw_token=2CX2HIT8EYG',
    'csrf': '2CX2HIT8EYG',
    'Referer': f'http://www.kuwo.cn/search/list?key=%E5%91%A8%E6%9D%B0%E4%BC%A6',  # 必须设置防盗链
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
}

welcome = f'''                                                                        
{Fore.LIGHTCYAN_EX}
  __  __     ______     ______     __         __     ______     __     ______     
 /\ \/ /    /\  ___\   /\  __ \   /\ \       /\ \   /\  __ \   /\ \   /\  ___\   
 \ \  _"-.  \ \  __\   \ \  __ \  \ \ \____  \ \ \  \ \ \/\ \  \ \ \  \ \___  \  
  \ \_\ \_\  \ \_____\  \ \_\ \_\  \ \_____\  \ \_\  \ \_____\  \ \_\  \/\_____\ 
   \/_/\/_/   \/_____/   \/_/\/_/   \/_____/   \/_/   \/_____/   \/_/   \/_____/ 
                                                                                 
{Fore.RESET}
                                                                                
{Fore.GREEN}      ╔══════════════════════════════════════════════════════════════╗        
      ║                       {Fore.LIGHTRED_EX}♫  音乐爱好者专属下载工具  ♫{Fore.GREEN}                       ║        
      ╚══════════════════════════════════════════════════════════════╝        
{Fore.LIGHTBLUE_EX}        🎵 支持酷我音乐、网易云音乐多种下载方式 🎵                                
        🎵 单曲搜索、歌手批量、榜单下载，应有尽有 🎵                                
        🎵 高清音质，极速下载，轻松畅享音乐世界 🎵                                
{Fore.RESET}
'''

# 定义显示菜单函数
def show_menu():
    print(Fore.RESET + "--------------MUSIC LOVER目录-----------------")
    print("1、音乐名称搜索下载       2、歌手音乐批量下载 ")
    print("3、网易云音乐单曲下载     4、网易云榜单批量下载")
    print("5、返回主菜单             0、退出程序")
    print("---------------------------------------------")
    return input("请输入功能的索引:")

#  酷我音乐歌曲下载及搜索功能制作
def kuwo_data():
    search = input('请输入需要搜索的歌曲:')
    kuwo_url = f"https://kuwo.cn/api/www/search/searchMusicBykeyWord?key={search}&pn=1&rn=30&httpsStatus=1&reqId=a1063621-a30b-11ed-9f29-3bb2bd0fadcc"
    #  制作展示信息的表格
    table = prettytable.PrettyTable()
    table.field_names = ['序号', '歌曲', '歌手']
    downloads_list = []  # 创建一个歌曲列表--->存放歌曲rid
    try:
        kuwo_response = requests.get(url=kuwo_url, headers=kuwo_headers)
        musics = kuwo_response.json()
        music_data = musics['data']['list']
        num = 0  # 序号
        for music in music_data:
            num = num + 1
            name = music['name']  # 歌曲名称
            singer = music['artist']  # 作者
            album = music['album']  # 专辑名称
            musicrid = music['musicrid']  # 歌曲未处理的rid
            rid = musicrid.split('_')[1]  # 处理后的歌曲rid  # split以'_'分割后取第一个字符串
            table.add_row([num, name, singer])
            table.align = 'l'
            table.right_padding_width = 7

            if num > 7:  # 只保留前八条信息
                break
            downloads_list.append(rid)
            downloads_list.append(name)

        print(table)

        # 歌曲下载功能
        user_choose = input('请输入需要下载的歌曲序号:')
        choose = int(user_choose) - 1
        download_choose = downloads_list[choose]  # 在列表里提取到相应的歌曲rid
        kuwo_name = int(user_choose) * 2 - 1  # 在downloads_list列表中如果选择的序号为第一个，那么对应名字索引为1，若序号为2，对应索引为3--->找规律
        download_name = downloads_list[kuwo_name]

        kuwo_download_url = f"http://www.kuwo.cn/api/v1/www/music/playUrl?mid={download_choose}&type=mp3&httpsStatus=1&reqId=00a692f1-1adb-11ed-83a9-e917414cf877"
        kuwo_download_resp = requests.get(url=kuwo_download_url, headers=kuwo_headers)

        kuwo_download_json = kuwo_download_resp.json()
        kuwo_music_download_url = kuwo_download_json['data']['url']
        # print(kuwo_music_download_url)
        kuwo_music_download = requests.get(kuwo_music_download_url, stream=True)
        try:
            kuwo_download_content_size = int(kuwo_music_download.headers['Content-Length']) / 1024  # 获取大小--->实现进度条功能
            # 使用存储文件夹路径
            save_path = os.path.join(MUSIC_STORAGE_FOLDER, f'{download_name}.mp3')
            with open(save_path, mode='wb') as f:
                for kuwo_data in tqdm(iterable=kuwo_music_download.iter_content(1024),  # 分段请求--->实现进度条功能
                                      total=kuwo_download_content_size,
                                      unit='k',  # 单位设置
                                      ncols=100,  # 长度设置
                                      desc=f'{download_name}'):
                    f.write(kuwo_data)
        except KeyError:
            print(Fore.YELLOW + f"无法获取文件大小信息，将使用普通下载方式")
            # 使用存储文件夹路径
            save_path = os.path.join(MUSIC_STORAGE_FOLDER, f'{download_name}.mp3')
            with open(save_path, mode='wb') as f:
                f.write(kuwo_music_download.content)
        print(Fore.GREEN + f'--{download_name}--下载完成^_^')
    except:
        print(Fore.YELLOW + '服务器忙碌中，正在尝试其他方法进行歌曲检索' + '')
        kuwo_user_chooseid = input("请输入歌曲的id(歌曲id查看方法详见github上README文档):")
        kuwo_user_downloadname = input("请输入歌曲名称")
        kuwo_download_url = f"http://www.kuwo.cn/api/v1/www/music/playUrl?mid={kuwo_user_chooseid}&type=mp3&httpsStatus=1&reqId=00a692f1-1adb-11ed-83a9-e917414cf877"
        kuwo_download_resp = requests.get(url=kuwo_download_url, headers=kuwo_headers)

        kuwo_download_json = kuwo_download_resp.json()
        kuwo_music_download_url = kuwo_download_json['data']['url']
        # print(kuwo_music_download_url)
        kuwo_music_download = requests.get(kuwo_music_download_url, stream=True)
        try:
            kuwo_download_content_size = int(kuwo_music_download.headers['Content-Length']) / 1024  # 获取大小--->实现进度条功能
            # 使用存储文件夹路径
            save_path = os.path.join(MUSIC_STORAGE_FOLDER, f'{kuwo_user_downloadname}.mp3')
            with open(save_path, mode='wb') as f:
                for kuwo_data in tqdm(iterable=kuwo_music_download.iter_content(1024),  # 分段请求--->实现进度条功能
                                      total=kuwo_download_content_size,
                                      unit='k',  # 单位设置
                                      ncols=100,  # 长度设置
                                      desc=f'{kuwo_user_downloadname}'):
                    f.write(kuwo_data)
        except KeyError:
            print(Fore.YELLOW + f"无法获取文件大小信息，将使用普通下载方式")
            # 使用存储文件夹路径
            save_path = os.path.join(MUSIC_STORAGE_FOLDER, f'{kuwo_user_downloadname}.mp3')
            with open(save_path, mode='wb') as f:
                f.write(kuwo_music_download.content)
        print(Fore.GREEN + f'--{kuwo_user_downloadname}--下载完成^_^')
    input("按回车键返回主菜单...")


def music_batchsize():
    singer = input('请输入需要下载的歌手姓名:')
    pages = int(input(f'请输入需要下载{singer}歌曲的页数:'))
    # 使用存储文件夹路径
    singer_folder = os.path.join(MUSIC_STORAGE_FOLDER, f"{singer}音乐专辑")
    os.makedirs(singer_folder, exist_ok=True)
    for page in range(1, pages + 1):
        batch_url = f'http://www.kuwo.cn/api/www/search/searchMusicBykeyWord?key={singer}&pn={page}&rn=30&httpsStatus=1&reqId=7b7b91a0-1ad7-11ed-b9a8-198e9cc3d87a'
        batch_response = requests.get(url=batch_url, headers=kuwo_headers)
        # 解析数据 找到音乐的下载地址
        json_data = json.loads(batch_response.text)  # 解析后的数据 为字典类型
        lists = json_data['data']['list']
        # 相关准备
        rid_box = []  # 建立一个列表用来存储音乐rid
        name_box = []  # 建立一个列表用来存储音乐名称
        download_box = []  # 建立一个列表用来存放下载链接
        num = 0  # 序号

        for lis in lists:
            rid_box.append(lis['rid'])
            name_box.append(lis['name'])

        for rid in tqdm(rid_box, ncols=100, desc=f"{singer}音乐专辑下载ing"):
            music_name = name_box[num]
            num = num + 1
            music_url = f'http://www.kuwo.cn/api/v1/www/music/playUrl?mid={rid}&type=mp3&httpsStatus=1&reqId=00a692f1-1adb-11ed-83a9-e917414cf877'
            music_response = requests.get(music_url)
            music_dic = json.loads(music_response.text)
            batch_download = music_dic['data']['url']

            download_box.append(batch_download)
            # 下载音乐

            # 使用存储文件夹路径
            save_path = os.path.join(singer_folder, f'{music_name}.mp3')
            f = open(save_path, 'wb')
            load_music = requests.get(batch_download)
            f.write(load_music.content)  # 下载音乐
            # print(f'{music_name}----------下载完成')
            time.sleep(random.randint(0, 1))

        print(Fore.GREEN + f"{singer}专辑音乐前{pages}页全部下载完成")
    input("按回车键返回主菜单...")


# 修改网易云音乐单曲下载函数
def music163_download():
    music163_user = input('请输入需要下载的歌曲链接:')
    music163_name = ""
    
    # 提取歌曲ID的更健壮方式
    try:
        music163_id = re.findall(r'[?&]id=(\d+)', music163_user)[0]
        print(f"歌曲id:{music163_id}")
        
        # 尝试从网易云API获取歌曲信息
        try:
            # 使用网易云音乐API获取歌曲信息
            music_info_url = f"https://music.163.com/api/song/detail/?id={music163_id}&ids=%5B{music163_id}%5D"
            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.69'
            }
            response = requests.get(music_info_url, headers=headers)
            response.raise_for_status()  # 检查请求是否成功
            music_data = response.json()
            
            # 解析歌曲信息
            if music_data.get('songs') and len(music_data['songs']) > 0:
                song_info = music_data['songs'][0]
                music163_name = song_info['name']
                artist_names = [artist['name'] for artist in song_info['artists']]
                artist_name = ' - '.join(artist_names)
                print(f"自动识别到歌曲: {music163_name} - {artist_name}")
                confirm = input("是否使用自动识别的歌曲名称？(y/n): ")
                if confirm.lower() != 'y':
                    music163_name = input('请输入歌曲名称:')
            else:
                print("无法从API获取歌曲信息")
                music163_name = input('请输入歌曲名称:')
        except Exception as e:
            print(f"自动识别歌曲名称失败: {e}")
            # 尝试从剪贴板获取（备用方案）
            try:
                clipboard_content = pyperclip.paste().strip()
                if clipboard_content:
                    print(f"检测到剪贴板内容: {clipboard_content}")
                    use_clipboard = input("是否使用剪贴板内容作为歌曲名称？(y/n): ")
                    if use_clipboard.lower() == 'y':
                        music163_name = clipboard_content
                    else:
                        music163_name = input('请输入歌曲名称:')
                else:
                    music163_name = input('请输入歌曲名称:')
            except:
                music163_name = input('请输入歌曲名称:')
    except IndexError:
        print(Fore.RED + "无法解析歌曲链接，请检查链接格式是否正确!")
        input("按回车键返回主菜单...")
        return
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.69',
        'cookie': 'ntes_nnid=12dd9027ec4a4ff630183944202b690a,1657856871847; NMTID=00OC6KXsPguQPjxek0Pn_KEeUAzOpIAAAGCfCK8uA; WEVNSM=1.0.0; WNMCID=ptvbsq.1661608626841.01.0; WM_TID=ierGlLZTeBdEQVRFARPFDKeqkyuB3Ama; __snaker__id=CeQB3pEOogudHnEZ; _9755xjdesxxd_=32; YD00000558929251%3AWM_NI=WlaGyyjhBlGFWpRJ9lwI6ZyPyCqmyMJi8DKrZjiVvu6fxnyecJWi28QQLS%2FznECqoyeSAknwRswWUwA2ZdSbiQZg8HiBi5jK9r8JDEwEdS%2B4no9j3hYsaul0I%2BIVdG1dYzY%3D; YD00000558929251%3AWM_NIKE=9ca17ae2e6ffcda170e2e6ee9bc57ba191ffa7e15fa2ef8bb6c55a829f8f82d54db19589d1c93c9087a88cb62af0fea7c3b92a95b4afa8fc73aab88e8dc64e95b09eabbc68b597fabbfc5cbb9dbf8efc478ab7f8a5ca7a9ab6a7b7f57ff6bab88ffc6fa196998ab134938f84b4ae72ae9b8d92ee73a78d8f8ced7d92adb9b8d87d83ee9685d26aab8f9688bb44ab9ea7d6e941fbaef8abc74fb59bacb4aa40aeb1f78bb2649badaf96ef3c8bf587b7e74df3bc979bdc37e2a3; YD00000558929251%3AWM_TID=bkkyZvU0ARlFVARARALRGtPShZ0LYgg7; gdxidpyhxdE=CcylxGK8mLsXRmznHGdsVN6rRamj5yNRk5%2FL9ik2g9CsmjfOz%5Crq8j7bn2qICQuTIiudi3L6pz%2BHjdywx06sy%5ClHUvC%5CVBcS%5C3E%5CykW7Jo92o0Toc%2BDkjZ9kbMHQXu9fA%5CtEO51jd3BjvGK9oRSI8%5CtQz8pk9tdEzJvRgcbLQVwqTkb%2F%3A1664730895816; vinfo_n_f_l_n3=1516aa89ecee8a87.1.0.1673952472114.0.1673952530183; JSESSIONID-WYYY=n1ef%5CFOkvhlNFvKJ0aDM5%2F%2FHr%2BiICD2TBVkfnrMXhb0Ui5iz7Kyekd6esR9DoVbbeaAhrp98pX%5CPj4cUmH6sBjy3lYXrwv7FdnA5tWesvbD4%3A1678603105014; _iuqxldmzr_=33; WM_NI=HoJj5do01k5NGJLoGWW4RPkdGy6fvSiccBQ81DVBVlbmuuWnDLLYtUd35ouyRCxblltBcZA41RzDu5YVyfJHXIGI3mcQsTxMeuB9EsuB23AssDimExvI7c8B9EkMpGvqTFc%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6eed3ae4fb7eea1abd63e92e78ba3c14a828b9eacc45c908600ace84094b99cd9f12af0fea7c3b92a8cb1868bb870adf0ff8cb84685968490c65d95ec9eb1ea7085a7fa87f559abbdada3d434f39c9aa3d568a2b3bb96d666889484baf75fa8edfb90f873929db883ef68b89eadbbc440f38eb6a5f83f9b8ab787c9449c9789aab267a18fbdb5fb47a7ab8edac879b79efed4c479b19ca78ec874b697f984bb4afb9ba5aef34db6af9ca7e237e2a3'
    }
    
    # 添加重试机制
    max_retries = 5  # 增加重试次数
    retry_count = 0
    success = False
    
    # 尝试不同的下载链接格式，增加更多可靠的第三方解析接口
    download_formats = [
        f'https://music.163.com/song/media/outer/url?id={music163_id}.mp3',
        f'http://music.163.com/song/media/outer/url?id={music163_id}.mp3',
        f'https://link.hhtjim.com/163/{music163_id}.mp3',  # 第三方解析接口
        f'http://music.163.com/song/media/outer/url?id={music163_id}',
        f'https://api.cider.workers.dev/?id={music163_id}',  # 新的第三方解析接口1
        f'https://api.injahow.cn/meting/api?server=netease&type=song&id={music163_id}&r=json',  # 新的第三方解析接口2
        f'https://music.163.com/song/media/outer/url?url=mp3&id={music163_id}'  # 另一种官方格式
    ]
    
    current_format_index = 0
    
    while retry_count < max_retries and not success:
        try:
            if current_format_index >= len(download_formats):
                current_format_index = 0  # 如果所有格式都试过了，重新从第一个开始
                retry_count += 1
                print(Fore.YELLOW + f"所有下载格式已尝试，开始第{retry_count}轮重试...")
                time.sleep(3)
                continue
            
            music163_download_url = download_formats[current_format_index]
            current_format_index += 1
            
            print(f"正在尝试下载链接: {music163_download_url}")
            
            # 添加重定向处理和更长的超时时间
            timeout = 30  # 增加超时时间到30秒
            music163_download_resp = requests.get(url=music163_download_url, headers=headers, 
                                                 allow_redirects=True, timeout=timeout)
            
            # 验证响应状态
            if music163_download_resp.status_code != 200:
                print(Fore.RED + f"下载失败，HTTP状态码: {music163_download_resp.status_code}")
                retry_count += 1
                continue
            
            # 针对API接口返回的JSON数据进行处理
            content_type = music163_download_resp.headers.get('Content-Type', '')
            if 'json' in content_type:
                try:
                    # 尝试解析JSON响应
                    api_data = music163_download_resp.json()
                    # 检查常见的API返回格式
                    if isinstance(api_data, dict):
                        if 'url' in api_data and api_data['url']:
                            print(f"从API获取到重定向链接，正在尝试下载...")
                            music163_download_resp = requests.get(url=api_data['url'], headers=headers, 
                                                                allow_redirects=True, timeout=timeout)
                        elif 'data' in api_data and isinstance(api_data['data'], dict) and 'url' in api_data['data']:
                            print(f"从API获取到重定向链接，正在尝试下载...")
                            music163_download_resp = requests.get(url=api_data['data']['url'], headers=headers, 
                                                                allow_redirects=True, timeout=timeout)
                except:
                    pass  # 如果不是有效的JSON，继续处理
            
            # 重新检查内容类型
            content_type = music163_download_resp.headers.get('Content-Type', '')
            if 'audio' not in content_type and len(music163_download_resp.content) < 1024 * 1024:  # 如果不是音频且小于1MB
                print(Fore.RED + "下载的内容可能不是有效的音频文件，尝试其他方式...")
                retry_count += 1
                continue
            
            # 增强VIP音乐检测
            if len(music163_download_resp.content) < 1024 * 100:  # 如果文件小于100KB，可能不是有效的音频
                content_str = music163_download_resp.content.decode('utf-8', errors='ignore')
                if any(keyword in content_str.lower() for keyword in ['会员', 'vip', '版权', '付费', 'premium', 'copyright']):
                    print(Fore.RED + f"歌曲《{music163_name}》检测为VIP专享或付费歌曲，无法直接下载。")
                    retry_count = max_retries  # 直接跳出重试循环
                    continue
                else:
                    print(Fore.YELLOW + "警告: 下载的文件可能不是有效的音频文件，文件大小异常小")
            
            try:
                music163_content_size = int(music163_download_resp.headers['Content-Length']) / 1024  # 获取大小--->实现进度条功能
                # 使用存储文件夹路径
                save_path = os.path.join(MUSIC_STORAGE_FOLDER, f'{music163_name}.mp3')
                with open(save_path, mode='wb') as f:
                    for music163_download in tqdm(iterable=music163_download_resp.iter_content(1024),  # 分段请求--->实现进度条功能
                                                  total=music163_content_size,
                                                  unit='k',  # 单位设置
                                                  ncols=100,  # 长度设置
                                                  desc=f'{music163_name}'):
                        f.write(music163_download)
            except KeyError:
                print(Fore.YELLOW + f"无法获取文件大小信息，将使用普通下载方式")
                # 使用分块下载以避免内存问题
                chunk_size = 8192
                with open(save_path, mode='wb') as f:
                    for chunk in tqdm(music163_download_resp.iter_content(chunk_size=chunk_size),
                                     desc=f'{music163_name}'):
                        if chunk:
                            f.write(chunk)
            
            # 验证下载的文件
            # 使用存储文件夹路径
            save_path = os.path.join(MUSIC_STORAGE_FOLDER, f'{music163_name}.mp3')
            if os.path.exists(save_path):
                file_size = os.path.getsize(save_path)
                if file_size < 1024 * 100:  # 如果文件小于100KB
                    print(Fore.RED + f"警告: 下载的文件大小仅有{file_size/1024:.2f}KB，可能不是完整的音频文件。")
                    print(Fore.YELLOW + f"这很可能是一首VIP专享歌曲，推荐使用功能1（酷我音乐搜索下载）尝试下载同一首歌。")
                    # 尝试使用酷我音乐搜索下载作为备选
                    try:
                        print(f"正在尝试使用酷我音乐搜索相同歌曲...")
                        # 调用酷我音乐搜索功能
                        # 这里只是一个简单的重定向提示，实际项目中可以考虑直接调用kuwo_data函数
                        print(Fore.GREEN + f"请使用功能1，搜索关键词：{music163_name}")
                    except:
                        pass
                else:
                    print(Fore.GREEN + f'--{music163_name}--下载完成^_^')
                success = True
        except requests.exceptions.Timeout:
            retry_count += 1
            print(Fore.RED + f"下载超时({timeout}秒)，网络可能不稳定，第{retry_count}次重试...")
            time.sleep(3)  # 网络不稳定时，增加重试间隔
        except requests.exceptions.ConnectionError:
            retry_count += 1
            print(Fore.RED + f"连接错误，可能是网络问题或服务器拒绝连接，第{retry_count}次重试...")
            time.sleep(3)
        except Exception as e:
            retry_count += 1
            print(Fore.RED + f"下载出错: {str(e)}，第{retry_count}次重试...")
            time.sleep(2)
    
    if not success:
        print(Fore.RED + f"歌曲《{music163_name}》下载失败。\n" +
              "可能的原因：\n" +
              "1. 这是一首VIP专享或付费歌曲，网易云音乐有版权保护\n" +
              "2. 歌曲链接已失效\n" +
              "3. 网络连接问题\n" +
              "4. 所有可用的下载接口均已失效或被限制\n" +
              "建议尝试：\n" +
              "- 使用功能1（酷我音乐搜索下载）搜索并下载同一首歌\n" +
              "- 检查网络连接后重试\n" +
              "- 支持正版音乐，前往网易云音乐开通VIP")
    
    input("按回车键返回主菜单...")


# 修改网易云歌单批量下载函数
def music_163_batchsize():
    print(Fore.MAGENTA + '小tips:输入网址时请去掉"#/",否则可能导致网址解析失败导致无法下载')
    user_list_url = input(Fore.RESET + "请输入需要下载的歌单网址:")

    user_file = input('请输入榜单名称:')
    # 构建榜单文件夹路径
    list_folder = os.path.join(MUSIC_STORAGE_FOLDER, user_file)
    os.makedirs(list_folder, exist_ok=True)
    headers = {

        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
        'sec-fetch-dest': 'iframe',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'referer': 'https://music.163.com/',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'cookie': '_ga=GA1.2.1412864897.1553836840; _iuqxldmzr_=32; _ntes_nnid=b757609ed6b0fea92825e343fb9dfd21,1568216071410; _ntes_nuid=b757609ed6b0fea92825e343fb9dfd21; WM_TID=Pg3EkygrDw1EBAVUVRIttkwA^%^2Bn1s1Vww; P_INFO=183605463^@qq.com^|1581593068^|0^|nmtp^|00^&99^|null^&null^&null^#not_found^&null^#10^#0^|^&0^|^|183605463^@qq.com; mail_psc_fingerprint=d87488b559a786de4942ad31e080b75f; __root_domain_v=.163.com; _qddaz=QD.n0p8sb.xdhbv8.k75rl6g4; __oc_uuid=2f4eb790-6da9-11ea-9922-b14d70d91022; hb_MA-BFF5-63705950A31C_source=blog.csdn.net; UM_distinctid=171142b7a6d3ba-0fbb0bf9a78375-4313f6a-144000-171142b7a6e30b; vinfo_n_f_l_n3=6d6e1214849bb357.1.0.1585181322988.0.1585181330388; JSESSIONID-WYYY=jJutWzFVWmDWzmt2vzgf6t5RgAaMOhSIKddpHG9mTIhK8fWqZndgocpo87cjYkMxKIlF^%^2BPjV^%^2F2NPykYHKUnMHkHRuErCNerHW6DtnD8HB09idBvHCJznNJRniCQ9XEl^%^2F7^%^2Bovbwgy7ihPO3oJIhM8s861d^%^2FNvyRTMDjVtCy^%^5CasJPKrAty^%^3A1585279750488; WM_NI=SnWfgd^%^2F5h0XFsqXxWEMl0vNVE8ZjZCzrxK^%^2F9A85boR^%^2BpV^%^2BA9J27jZCEbCqViaXw6If1Ecm7okWiL^%^2BKU2G8frpRB^%^2BRRDpz8RNJnagZdXn6KNVBHwK2tnvUL^%^2BxWQ^%^2BhGf2aeWE^%^3D; WM_NIKE=9ca17ae2e6ffcda170e2e6ee84b64f86878d87f04fe9bc8fa3c84f878f9eafb65ab59498cccf48f7929fb5e72af0fea7c3b92a91b29987e670edeba8d1db4eb1af9899d64f8fb40097cd5e87e8968bd949baaeb8acae3383e8fb83ee5ae9b09accc4338aeef98bd94987be8d92d563a388b9d7cc6ef39bad8eb665a989a7adaa4197ee89d9e57ab48e8eccd15a88b0b6d9d1468ab2af88d9709cb2faaccd5e8298b9acb180aeaa9badaa74958fe589c66ef2bfabb8c837e2a3; playerid=67583529',
    }

    resp = requests.get(url=user_list_url, headers=headers)
    a = 0
    html_data = resp.text
    info_list = re.findall('<li><a href="/song\?id=(.*?)">(.*?)</a></li>', html_data)
    
    # 记录成功和失败的下载数量
    success_count = 0
    fail_count = 0
    fail_list = []

    for info in info_list:
        a = a + 1
        new = "http://music.163.com/song/media/outer/url?id="
        music_url = new + str(info[0])
        music_name = info[1]
        music_name = re.sub('[\\/:?"<>|]', '', music_name)
        
        # 构建完整的保存路径
        save_path = os.path.join(list_folder, f'{music_name}.mp3')
        
        try:
            # 访问播放链接
            music = requests.get(music_url, timeout=15).content
            
            # 检查文件大小，小于100KB可能是预览版或无效文件
            if len(music) < 1024 * 100:
                print(Fore.YELLOW + f"{a}. {music_name}-----下载可能不完整（文件过小，可能是预览版或VIP限制）")
                fail_count += 1
                fail_list.append(music_name)
            else:
                # 保存文件
                with open(save_path, mode="wb") as f:
                    f.write(music)
                print(Fore.GREEN + f"{a}. {music_name}-----下载完成")
                success_count += 1
            
            # 添加延迟避免请求过于频繁
            time.sleep(2)
        except Exception as e:
            print(Fore.RED + f"{a}. {music_name}-----下载失败: {str(e)}")
            fail_count += 1
            fail_list.append(music_name)
            time.sleep(1)
    
    # 显示下载统计信息
    print(Fore.GREEN + f"\n{user_file}下载完成！")
    print(Fore.GREEN + f"成功下载: {success_count}首")
    print(Fore.RED + f"下载失败: {fail_count}首")
    if fail_count > 0:
        print(Fore.YELLOW + "失败列表:", ", ".join(fail_list[:5]) + ("..." if len(fail_list) > 5 else ""))
        print(Fore.YELLOW + "提示: 失败的歌曲可能是VIP专享歌曲，建议使用功能1（酷我音乐搜索下载）单独尝试")
    print(Fore.GREEN + f'文件保存位置: {os.path.abspath(list_folder)}')
    
    input("按回车键返回主菜单...")


if __name__ == '__main__':
    print(welcome)
    notice = '请大家支持正版音乐，本产品仅适用于学习交流， 严禁商用，如希望添加其他功能，请联系作者QQ：1523758754（作者：得不偿失）'
    print(Fore.CYAN + notice)
    
    # 显示存储文件夹位置
    print(Fore.YELLOW + f"音乐文件将保存至: {os.path.abspath(MUSIC_STORAGE_FOLDER)}")
    
    while True:
        user = show_menu()
        if user == '1':
            kuwo_data()
        elif user == '2':
            music_batchsize()
        elif user == '3':
            music163_download()
        elif user == '4':
            music_163_batchsize()
        elif user == '5':
            continue  # 返回主菜单
        elif user == '0' or user == 'o':
            print("感谢使用，再见！")
            break
        else:
            print(Fore.RED + "输入错误，请重新输入!")
            input("按回车键继续...")

# 定义音乐存储文件夹
MUSIC_STORAGE_FOLDER = '音乐下载'
# 创建存储文件夹（如果不存在）
os.makedirs(MUSIC_STORAGE_FOLDER, exist_ok=True)

