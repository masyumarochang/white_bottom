import sys
import pygame
import random
import asyncio

import os
from pyodide.http import pyfetch

current_bgm = None


ASSETS = [
    "background/background_nihil.png",
    "background/background_MONO.png",
    "background/background_R.png",
    "background/background_G.png",
    "background/background_B.png",
    "nihil_mono.png",
    "nihil_red.png",
    "nihil_blue.png",
    "nihil_green.png",
    "nihil_fullcolor.png",
    "nihil_red_dark.png",
    "nihil_blue_sad.png",
    "nihil_green_sad.png",
    "nihil_highlight.png",
    "bgm/cafe.ogg",
    "bgm/green.ogg",
    "bgm/blue.ogg",
    "ZenKakuGothicNew-Medium.ttf",
    "se/elevator.mp3",
    "se/typing.mp3",
    "se/selected.mp3",
    ]

async def fetch_assets():
    for path in ASSETS:
        folder = os.path.dirname(path)
        if folder:
            os.makedirs(folder, exist_ok=True)
        res = await pyfetch(path)
        if not res.ok:
            raise FileNotFoundError(f"取得失敗: {path} ({res.status})")
        with open(path, "wb") as f:
            f.write(await res.bytes())

async def main():
    print("初期化してるよー")

    await fetch_assets()

    pygame.init()
    pygame.mixer.init()

    SE_DICT = {
        "elevator": pygame.mixer.Sound("se/elevator.mp3"),
        "typing": pygame.mixer.Sound("se/typing.mp3"),
        "selected": pygame.mixer.Sound("se/selected.mp3"),
    }
    SE_DICT["typing"].set_volume(0.3)
    SE_DICT["selected"].set_volume(0.8)

    print("画面生成してるよー")

    SCREEN_WIDTH = 640
    SCREEN_HEIGHT = 480
    screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
    pygame.display.set_caption("白色の底ーtest")

    BG_COLOR = (240,240,240)
    TEXT_COLOR = (255,255,255)


    def play_bgm(file_name, volume=0.5, fade_ms=1000):
        global current_bgm
        if current_bgm == file_name:
            return
        
        current_bgm = file_name
        pygame.mixer.music.stop()
        
        if file_name: 
            pygame.mixer.music.load(file_name)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1, fade_ms=fade_ms) 



    bg_images = {
        "FULL": pygame.transform.scale(
            pygame.image.load("background/background_nihil.png").convert(),
            (SCREEN_WIDTH, SCREEN_HEIGHT),
        ),
        "MONO": pygame.transform.scale(
            pygame.image.load("background/background_MONO.png").convert(),
            (SCREEN_WIDTH, SCREEN_HEIGHT),
        ),
        "RED": pygame.transform.scale(
            pygame.image.load("background/background_R.png").convert(),
            (SCREEN_WIDTH, SCREEN_HEIGHT),
        ),
        "GREEN": pygame.transform.scale(
            pygame.image.load("background/background_G.png").convert(),
            (SCREEN_WIDTH, SCREEN_HEIGHT),
        ),
        "BLUE": pygame.transform.scale(
            pygame.image.load("background/background_B.png").convert(),
            (SCREEN_WIDTH, SCREEN_HEIGHT),
        ),
    }

    current_bg_key = "FULL"


    
    font = pygame.font.Font("ZenKakuGothicNew-Medium.ttf", 20)
    title_font = pygame.font.Font("ZenKakuGothicNew-Medium.ttf", 36)

    system_flags = {
        "B" : False,
        "R" : False,
    }

    IMG_PATHS = {
        "MONO" : "nihil_mono.png",
        "RED" : "nihil_red.png",
        "BLUE" : "nihil_blue.png",
        "GREEN" : "nihil_green.png",
        "FULLCOLOR" : "nihil_fullcolor.png",

        "RED_DARK" : "nihil_red_dark.png",
        "BLUE_SAD" : "nihil_blue_sad.png",
        "GREEN_SAD" : "nihil_green_sad.png",
        "HIGHLIGHT" : "nihil_highlight.png",
    }

    chara_images = {}
    for key, path in IMG_PATHS.items():
        try:
            img = pygame.image.load(path).convert_alpha()
            orig_w, orig_h = img.get_size()
            target_h = 500
            target_w = int(orig_w * (target_h / orig_h))
            chara_images[key] = pygame.transform.smoothscale(img, (target_w, target_h))
        except (FileNotFoundError, pygame.error):
            dummy = pygame.Surface((200, 500), pygame.SRCALPHA)
            color_box = {
                "MONO": (120, 120, 120), "RED": (200, 60, 60), "RED_DARK": (120, 20, 20),
                "GREEN": (60, 180, 60), "GREEN_SAD": (40, 100, 60),
                "BLUE": (60, 60, 200), "BLUE_SAD": (40, 40, 120),
                "FULLCOLOR": (240, 200, 80), "HIGHLIGHT": (255, 255, 255)
            }.get(key, (100, 100, 100))
            
            dummy.fill((0, 0, 0, 160))
            pygame.draw.rect(dummy, color_box, (5, 5, 190, 350), 3)
            txt = font.render(f"[{key}]", True, (255, 255, 255))
            dummy.blit(txt, (20, 170))
            
            chara_images[key] = dummy

    def get_current_chara_key(active_route, scenario_img_tag):
        """
        シナリオデータ内のimgタグになんか指定されてたらそっち優先するけど、
        "NORMAL"とかデフォルト指定やったら現在のルートに合わせて絵を表示するやで！
        """

        if scenario_img_tag in IMG_PATHS:
            return scenario_img_tag

        if active_route == "WHITE":
            return "FULLCOLOR"
        elif active_route in ("RED","KURENAI"):
            return "RED"
        elif active_route in ("GREEN", "CYAN"):
            return "GREEN"
        elif active_route == "BLUE":
            return "BLUE"
        elif active_route == "BLACK":
            return "MONO"
        return "MONO"

    #  シナリオ　ここから　- - - - - - - - - - - - - - - - -    

    scenario_prologue = [
        {"img" : "NORMAL", "bg":"MONO", "text" : "「いらっしゃいませ。喫茶RGBへようこそ」"},
        {"img" : "NORMAL", "bg":"MONO", "text" : "「...ああ、久しぶりのお客様でして」"},
        {"img" : "NORMAL", "bg":"MONO", "text" : "「ご注文はどうなさいますか」"},
    ]

    scenario_red = [
        {"img" : "NORMAL", "bg":"RED", "text" : "「お待たせしました。深掘りするのは...おすすめしません。」"},
        {"img" : "NORMAL", "bg":"RED", "text" : "「本当に良くない。人間皆、そうなってしまうのですね。」"},
        {"img" : "RED_DARK", "bg":"RED", "text" : "「...失望しました。」"},
        {"img" : "NORMAL", "bg":"RED", "text" : "(ーなんだろう...なんだか生温い、熱い感覚が...)"},
        {"img" : "NORMAL", "bg":"RED", "text" : "【BAD END1 /R/ 堕ちてゆきましょう】"},
    ]

    scenario_kurenai_end = [
        {"img" : "NORMAL", "bg":"RED", "text" : "「あーあ。ちょっと分けてあげたのですから、最後まで残さず食べてくださいね。」"},
        {"img" : "RED_DARK", "bg":"RED", "text" : "(ー視界がぼやけ、意識が遠のいていく...)"},
        {"img" : "RED_DARK", "bg":"RED", "text" : "「また来てくださいね。」"},
        {"img" : "NORMAL", "bg":"RED", "text" : "【BAD END2 /CRIMSON/ 思い出の一品】"},
    ]

    scenario_kurenai_talk = [
        {"img" : "NORMAL", "bg":"RED", "text" : "「お待たせいたしました。」"},
        {"img" : "NORMAL", "bg":"RED", "text" : "「ふふふ。アレ、気になりますか？非売品ですよ。」"},
        {"img" : "NORMAL", "bg":"RED", "text" : "「...できるだけもう少し取っておきたかったのですが...」"},
    ]

    scenario_green = [
        {"img" : "NORMAL", "bg":"GREEN", "text" : "「お待たせいたしました。」"},
        {"img" : "GREEN_SAD", "bg":"GREEN", "text" : "「さっさと帰ってください。送り届けはしませんが。」"},
        {"img" : "GREEN_SAD", "bg":"GREEN", "text" : "「あのモノのようになっては、私が困るのです。」"},
        {"img" : "NORMAL", "bg":"GREEN","se" : "elevator", "text" : "(到着したエレベーターの扉の奥から、重苦しい空気が漂ってくる...)"},
        {"img" : "NORMAL", "bg":"GREEN", "text" : "「お気を付けて。絶対にまた来ないでくださいね。」"},
        {"img" : "NORMAL", "bg":"GREEN", "text" : "【 NORMAL END /GREEN/ 今すぐにこのゲームを閉じてください】"},
    ]

    scenario_cyan = [
        {"img" : "NORMAL", "bg":"GREEN", "text" : "「お待たせしました。」"},
        {"img" : "NORMAL", "bg":"GREEN", "text" : "「店内の雰囲気には慣れましたか？」"},
        {"img" : "NORMAL", "bg":"GREEN", "text" : "「知ろうとすることは、良いことです。」"},
        {"img" : "NORMAL", "bg":"GREEN", "text" : "「それが、不幸を招くことになってしまうことがある。」"},
        {"img" : "NORMAL", "bg":"GREEN", "text" : "「...ありました。」"},
        {"img" : "NORMAL", "bg":"GREEN", "text" : "「何でもないです。さっさと帰ってください。」"},
        {"img" : "NORMAL", "bg":"GREEN", "text" : "【 LUCKY END /CYAN/ 果汁33%】"},
    ]

    scenario_black = [
        {"img": "NORMAL", "bg":"MONO", "text": "「何も頼まないのは客ではありませんよ」"},
        {"img": "NORMAL", "bg":"MONO", "text": "「帰すわけにもいきませんから。」"},
    ]

    scenario_black_end = [
        {"img": "NORMAL", "bg":"MONO", "text": "「変わりませんね。」"},
        {"img": "NORMAL", "bg":"MONO", "text": "（ー視界が急速に黒く染まっていく...）"},
        {"img": "NORMAL", "bg":"MONO", "text": "「...何度でも来てくださいね。」"},
        {"img": "NORMAL", "bg":"MONO", "text": "【 BAD END3 /BLACK/またのご来店を 】"},
    ]

    scenario_blue = [
        {"img": "NORMAL", "bg":"BLUE", "text": "「お待たせしました。他には？」"}
    ]

    scenario_blue_end = [
        {"img": "BLUE_SAD", "bg":"BLUE", "text": "「ここはこの紅茶のような青い地球の、底の底です。」"},
        {"img": "BLUE_SAD", "bg":"BLUE", "text": "「私はあなたのような、愚かなモノを利用して生きているのですよ」"},
        {"img": "NORMAL", "bg":"BLUE", "text": "「ショックですかね。可哀想に。」"},
        {"img": "NORMAL", "bg":"BLUE", "text": "「まあ、あのモノよりかは幸せになることでしょう...」"},
        {"img": "NORMAL", "bg":"BLUE", "text": "「...というか、しなければならない。そんな気がして。」"},
        {"img": "NORMAL", "bg":"BLUE", "se": "elevator", "text": "（エレベーターが開き、繝九ヲ繝ｫが静かに送り届ける）"},
        {"img": "NORMAL", "bg":"BLUE", "text": "「まあ、お気をつけて。また来ないでください。」"},
        {"img": "NORMAL", "bg":"BLUE", "text": "【 TRUE END? /BLUE/ きっと見つけられる 】"},
    ]

    scenario_white_start = [
        {"img": "NORMAL", "bg":"FULL", "text": "「あはは...知らなければ良いことだってあるのに...」"},
        {"img": "NORMAL", "bg":"FULL", "text": "（店内を満たしていたすべての色が、静かに戻っていく...）"},
        {"img": "NORMAL", "bg":"FULL", "text": "「面白いですね。気に入りました。」"}
    ]

    scenario_white_end = [
        {"img": "HIGHLIGHT", "bg":"FULL", "text": "「ああ、このモノは実に、面白いなぁ...」"},
        {"img": "HIGHLIGHT", "bg":"FULL", "text": "「私のような地底人は到底理解できないと思っていましたが...」"},
        {"img": "HIGHLIGHT", "bg":"FULL", "text": "「...いいでしょう。外のこと、教えてください。」"},
        {"img": "HIGHLIGHT", "bg":"FULL", "se": "elevator", "text": "（エレベーターが到着し、二人は共に乗り込んだ――）"},
        {"img": "HIGHLIGHT", "bg":"FULL", "text": "【 SECRET TRUE END /WHITE/あなたとならBREAK TIME 】"},
    ]

    #   ここまで - - - - - - - - - - - - - - - - - - - - - - - - - -
    active_route = "PROLOGUE"
    scene = "TITLE"
    current_scenario = scenario_prologue
    script_index = 0
    displayed_char_count = 0
    TEXT_SPEED = 2
    frame_counter = 0
    current_full_text = ""
    current_data = current_scenario[0]
    show_item_text_timer = 0

    msg_window_rect = pygame.Rect(20,340,600,120)
    msg_window_surface = pygame.Surface((600,120),pygame.SRCALPHA)
    msg_window_surface.fill((0,0,0,200))

    btn_red = pygame.Rect(170,130,300,45)
    btn_green = pygame.Rect(170,190,300,45)
    btn_blue = pygame.Rect(170,250,300,45)
    btn_all = pygame.Rect(170,260,300,40)

    obj_knife = pygame.Rect(50,200,100,100)
    obj_pickles = pygame.Rect(270,200,100,100)
    obj_coffee = pygame.Rect(490,200,100,100)
    btn_wait = pygame.Rect(240,320,260,40)

    btn_choice1 = pygame.Rect(170,160,300,45)
    btn_choice2 = pygame.Rect(170,230,300,45)

    clock = pygame.time.Clock()
    running = True
    selected_menu = None
    current_node = current_scenario[script_index]

    if "bg" in current_node:
        current_bg_key = current_node["bg"]

    print("アセットとか読み込んだよー")



    while running:
        current_node = current_scenario[script_index]

        if "bg" in current_node:
            current_bg_key = current_node["bg"]

        screen.blit(bg_images[current_bg_key], (0, 0))

        if scene == "CHOICE":
            choice_timer += clock.get_time() / 1000.0
            if choice_timer >= 60.0 and not system_flags.get("SHOW_ALL_OPTION"):
                active_route = "BLACK"
                scene = "GAME"
                current_scenario = scenario_black
                script_index = 0
                displayed_char_count = 0

        if scene == "BLUE_ORDER_CHOICE":
            blue_order_timer += clock.get_time() / 1000.0

        if scene == "GAME":
            current_data = current_scenario[script_index]
            current_full_text = current_data["text"]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN or (
                event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN)
            ):
                if scene == "TITLE":
                    play_bgm(None)
                    active_route = "PROLOGUE"
                    scene = "GAME"
                    current_scenario = scenario_prologue
                    script_index = 0
                    displayed_char_count = 0
                    choice_timer = 0
                    kurenai_alpha = 0.0
                    play_bgm("bgm/cafe.ogg")

                elif scene == "GAME":
                    if displayed_char_count < len(current_full_text):
                        displayed_char_count = len(current_full_text)
                    else:
                        if script_index < len(current_scenario) - 1:
                            script_index += 1
                            displayed_char_count = 0
                            current_data = current_scenario[script_index]
                            se_key = current_data.get("se")
                            if se_key and se_key in SE_DICT:
                                SE_DICT[se_key].play()
                            
                        else:
                            if current_scenario == scenario_prologue:
                                scene = "CHOICE"
                                choice_timer = 0
                            elif current_scenario == scenario_black:
                                scene = "BLACK_YES_NO"
                            elif current_scenario == scenario_kurenai_talk:
                                scene = "KURENAI_CHOICE"
                            elif current_scenario == scenario_cyan:
                                scene = "TITLE"
                            elif current_scenario == scenario_blue:
                                scene = "BLUE_ORDER_CHOICE"
                                blue_order_timer = 0
                            elif current_scenario == scenario_white_start:
                                scene = "WHITE_CHOICE"
                            elif current_scenario in (scenario_red, scenario_kurenai_end, scenario_green, scenario_black_end, scenario_blue_end, scenario_white_end):
                                if current_scenario == scenario_red:
                                    system_flags["R"] = True
                                elif current_scenario == scenario_blue_end:
                                    system_flags["B"] = True
                                scene = "TITLE"
                elif scene == "CHOICE":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        m = event.pos
                        if btn_red.collidepoint(m):
                            if "selected" in SE_DICT:
                                SE_DICT["selected"].play()
                            selected_menu = "RED"
                            pickles_count = 0
                            examined_item = {"knife": False, "pickles": False, "coffee": False}
                            scene = "SEARCH"
                        elif btn_green.collidepoint(m):
                            if "selected" in SE_DICT:
                                SE_DICT["selected"].play()
                            selected_menu = "GREEN"
                            pickles_count = 0
                            examined_item = {"knife": False, "pickles": False, "coffee": False}
                            scene = "SEARCH"
                        elif btn_blue.collidepoint(m) and system_flags["R"]:
                            if "selected" in SE_DICT:
                                SE_DICT["selected"].play()
                            selected_menu = "BLUE"
                            pickles_count = 0
                            examined_item = {"knife": False, "pickles": False, "coffee": False}
                            scene = "SEARCH"
                        elif system_flags.get("SHOW_ALL_OPTION") and btn_all.collidepoint(m):
                            if "selected" in SE_DICT:
                                SE_DICT["selected"].play()
                            active_route = "WHITE"
                            current_scenario = scenario_white_start
                            script_index = 0
                            displayed_char_count = 0
                            scene = "GAME"
                elif scene == "SEARCH":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        m = event.pos
                        if obj_knife.collidepoint(m):
                            if "selected" in SE_DICT:
                                SE_DICT["selected"].play()
                            examined_item["knife"] = True
                            current_item_text = "「ナイフだ。切れ味がよさそうな、新しいものに見える。」"
                            show_item_text_timer = 120
                        elif obj_pickles.collidepoint(m):
                            if "selected" in SE_DICT:
                                SE_DICT["selected"].play()
                            examined_item["pickles"] = True
                            current_item_text = "「瓶詰めになったピクルスだ。漬けてあるものはわからない。」"
                            show_item_text_timer = 120
                            pickles_count += 1
                        elif obj_coffee.collidepoint(m):
                            if "selected" in SE_DICT:
                                SE_DICT["selected"].play()
                            examined_item["coffee"] = True
                            current_item_text = "「コーヒー豆を自動で挽く新しい機械だ。ここにこんなものが？」"
                            show_item_text_timer = 120
                        elif btn_wait.collidepoint(m):
                            if "selected" in SE_DICT:
                                SE_DICT["selected"].play()
                            print("待つボタン押されたやで")
                            if selected_menu == "RED":
                                if pickles_count >= 3:
                                    active_route = "KURENAI"
                                    current_scenario = scenario_kurenai_talk
                                else:
                                    active_route = "RED"
                                    current_scenario = scenario_red
                                script_index = 0
                                displayed_char_count = 0
                                scene = "GAME"
                            elif selected_menu == "GREEN":
                                play_bgm("bgm/green.ogg")
                                all_examined = all(examined_item.values())
                                cyan_chance = random.randint(1,3)
                                print(cyan_chance)
                                if all_examined and cyan_chance == 1:
                                    active_route = "CYAN"
                                    current_scenario = scenario_cyan
                                    print("CYANルートに進むやで")
                                else:
                                    active_route = "GREEN"
                                    current_scenario = scenario_green
                                    print("GREENルートに進むやで")

                                # ★ CYANでもGREENでも共通で必要な初期化＆画面切り替え！
                                script_index = 0
                                displayed_char_count = 0
                                current_full_text = current_scenario[script_index]
                                scene = "GAME"  # ★ これで絶対に GAME 画面に切り替わります！

                                print(f"【遷移完了】route={active_route}, scene={scene}, text={current_full_text}")
                            elif selected_menu == "BLUE":
                                active_route = "BLUE"
                                play_bgm("bgm/blue.ogg")
                                current_scenario = scenario_blue
                                script_index = 0
                                displayed_char_count = 0
                                scene = "GAME"

                elif scene == "BLACK_YES_NO":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if btn_choice1.collidepoint(event.pos) or btn_choice2.collidepoint(event.pos):
                            if "selected" in SE_DICT:
                                SE_DICT["selected"].play()
                            active_route = "BLACK"
                            current_scenario =  scenario_black_end
                            script_index = 0
                            displayed_char_count = 0
                            scene = "GAME"
                elif scene == "KURENAI_CHOICE":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if btn_choice1.collidepoint(event.pos):
                            if "selected" in SE_DICT:
                                SE_DICT["selected"].play()
                            kurenai_alpha = 0.0
                            current_scenario = scenario_kurenai_end
                            script_index = 0
                            displayed_char_count = 0
                            scene = "GAME"
                        elif btn_choice2.collidepoint(event.pos):
                            if "selected" in SE_DICT:
                                SE_DICT["selected"].play()
                            active_route = "RED"
                            current_scenario = scenario_red
                            script_index = 0
                            displayed_char_count = 0
                            scene = "GAME"

                elif scene == "BLUE_ORDER_CHOICE":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        # 1. 「いらないです」を押した場合
                        if btn_choice1.collidepoint(event.pos):
                            if "selected" in SE_DICT:
                                SE_DICT["selected"].play()
                            print("→ 『いらないです』を選択：青ルート継続")
                            current_scenario = scenario_blue_end
                            script_index = 0
                            displayed_char_count = 0
                            scene = "GAME"

                        # 2. 「全部ください」を押した場合
                        elif btn_choice2.collidepoint(event.pos):
                            if "selected" in SE_DICT:
                                SE_DICT["selected"].play()
                            print(f"→ 『全部ください』をクリック！ (タイマー: {blue_order_timer:.1f}秒)")
                            
                            # 10秒経過している時だけ白ルートへ！
                            if blue_order_timer >= 10.0:
                                play_bgm("bgm/cafe.ogg")
                                print("★ 条件達成！ 白ルートへ移動します！")
                                active_route = "WHITE"
                                current_scenario = scenario_white_start
                                script_index = 0
                                displayed_char_count = 0
                                scene = "GAME"
                            else:
                                print("※まだ10秒経っていないためボタンは機能しません")
                elif scene == "WHITE_CHOICE":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if btn_choice1.collidepoint(event.pos):
                            if "selected" in SE_DICT:
                                SE_DICT["selected"].play()
                            print("→ 『一緒に帰りませんか』を選択：白ルート継続")
                            active_route = "WHITE"
                            current_scenario = scenario_white_end
                            script_index = 0
                            displayed_char_count = 0
                            scene = "GAME"
                        elif btn_choice2.collidepoint(event.pos):
                            if "selected" in SE_DICT:
                                SE_DICT["selected"].play()
                            active_route = "BLUE"
                            current_scenario = scenario_blue_end
                            script_index = 0
                            displayed_char_count = 0
                            scene = "GAME"
                
        if scene == "GAME" and displayed_char_count < len(current_full_text):
            frame_counter += 1
            if frame_counter >= TEXT_SPEED:
                displayed_char_count += 1
                frame_counter = 0
                if "typing" in SE_DICT:
                    if displayed_char_count %2 == 0:
                        SE_DICT["typing"].play()

        if scene == "TITLE":
            play_bgm(None)
            screen.fill((20,20,20))
            t_text = title_font.render("白色の底",True, (255,255,255))
            s_text = font.render("- CLICK TO START -",True, (180,180,180))
            screen.blit(t_text, (240, 180))
            screen.blit(s_text, (225, 280))

        elif scene == "GAME" :
            screen.fill(BG_COLOR)
            screen.blit(bg_images[current_bg_key], (0, 0))
                            

            chara_key = get_current_chara_key(active_route, current_data.get("img"))
            current_img = chara_images[chara_key]

            # 画像の位置（Rect）を取得して計算
            img_rect = current_img.get_rect()
            
            # ① 左右の中央に配置
            img_rect.centerx = SCREEN_WIDTH // 2
            
            # ② 下端の位置を設定（沈め具合の調整）
            # SCREEN_HEIGHT + 80 にすると、足元が 80px 画面下に沈みます！
            img_rect.bottom = SCREEN_HEIGHT + 100

            # 描画は1回だけ！
            screen.blit(current_img, img_rect)

            total_steps = len(current_scenario)
            progress = script_index / max(1, total_steps - 1)

            if current_scenario == scenario_red:
                play_bgm(None)
                overlay = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT), pygame.SRCALPHA)
                alpha = int(progress * 180)
                overlay.fill((200, 20, 20, alpha))
                screen.blit(overlay, (0,0))
            elif current_scenario == scenario_black_end:
                play_bgm(None)
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                alpha = int(progress * 245)
                overlay.fill((0,0,0,alpha))
                screen.blit(overlay,(0,0))
            elif current_scenario == scenario_kurenai_end:
                play_bgm(None)
                if kurenai_alpha < 230:
                    kurenai_alpha += 0.3
                overlay = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((120, 10, 40 ,int(kurenai_alpha)))
                screen.blit(overlay,(0,0))

            screen.blit(msg_window_surface, (20,340))
            pygame.draw.rect(screen, (255,255,255),msg_window_rect,2)

            if isinstance(current_full_text, dict):
                target_text = current_full_text["text"]
        # ※もし立ち絵の切り替え処理もここで行うなら：
        # current_chara_img = current_full_text.get("img", "NORMAL")
            else:
                target_text = current_full_text

            visible_text = target_text[:displayed_char_count]
            text_surface = font.render(visible_text, True, TEXT_COLOR)
            screen.blit(text_surface,(40,360))

        elif scene == "CHOICE":
            screen.fill((30,30,30))
            ask_text = font.render("「ご注文はどうなさいますか」",True, (255,255,255))
            screen.blit(ask_text, (210,60))

            pygame.draw.rect(screen, (180,50,50), btn_red,border_radius=6)
            screen.blit(font.render("1. イチゴのパフェ", True,(255,255,255)),(btn_red.x + 20,btn_red.y + 10))

            pygame.draw.rect(screen,(50,150,50),btn_green, border_radius=6)
            screen.blit(font.render("2. メロンソーダ", True,(255,255,255)),(btn_green.x + 20,btn_green.y + 10))

            if system_flags["R"]:
                pygame.draw.rect(screen,(50,50,180),btn_blue, border_radius=6)
                screen.blit(font.render("3. バタフライピー", True,(255,255,255)),(btn_blue.x + 20,btn_blue.y + 10))
            else:
                pygame.draw.rect(screen,(70,70,70),btn_blue, border_radius=6)
                screen.blit(font.render("3. ????", True,(150,150,150)),(btn_blue.x + 20,btn_blue.y + 10))
                
            if choice_timer > 10.0 and system_flags.get("B"):
                system_flags["SHOW_ALL_OPTION"] = True


        elif scene == "SEARCH":
            screen.fill((40,35,30))
            guide_txt = font.render("注文を待つ間、店内を見渡す...", True,(220,220,220))
            screen.blit(guide_txt,(30,20))

            pygame.draw.rect(screen, (120, 120, 140), obj_knife, border_radius=8)
            screen.blit(font.render("ナイフ", True, (255, 255, 255)), (obj_knife.x + 22, obj_knife.y + 40))

            # 瓶詰め（高さ100の四角）
            pygame.draw.rect(screen, (40, 120, 60), obj_pickles, border_radius=8)
            screen.blit(font.render("瓶詰め", True, (255, 255, 255)), (obj_pickles.x + 22, obj_pickles.y + 30))
            screen.blit(font.render(f"({pickles_count}回)", True, (200, 200, 200)), (obj_pickles.x + 25, obj_pickles.y + 55))

            # コーヒーマシン（2行に分けて中央寄りに配置）
            pygame.draw.rect(screen, (140, 90, 50), obj_coffee, border_radius=8)
            screen.blit(font.render("コーヒー", True, (255, 255, 255)), (obj_coffee.x + 15, obj_coffee.y + 30))
            screen.blit(font.render("マシン", True, (255, 255, 255)), (obj_coffee.x + 22, obj_coffee.y + 55))

            # 席で待つ（高さ40の横長ボタン）
            pygame.draw.rect(screen, (100, 100, 100), btn_wait, border_radius=6)
            screen.blit(font.render("席で待つ", True, (255, 255, 255)), (btn_wait.x + 45, btn_wait.y + 10))

            if show_item_text_timer > 0:
                show_item_text_timer -= 1
                screen.blit(msg_window_surface,(20,370))
                screen.blit(font.render(current_item_text,True,TEXT_COLOR),(40,390))

        elif scene == "BLACK_YES_NO":
            screen.fill((10,10,10))
            pygame.draw.rect(screen,(80,80,80),btn_choice1,border_radius=6)
            pygame.draw.rect(screen,(80,80,80),btn_choice2,border_radius=6)
            screen.blit(font.render("はい",True,(255,255,255)),(btn_choice1.x+130,btn_choice1.y+12))
            screen.blit(font.render("いいえ",True,(255,255,255)),(btn_choice2.x+120,btn_choice2.y+12))

        elif scene == "KURENAI_CHOICE":
            screen.fill((30,20,20))
            pygame.draw.rect(screen,(150,40,40),btn_choice1,border_radius=6)
            pygame.draw.rect(screen,(80,80,80),btn_choice2,border_radius=6)
            screen.blit(font.render("どうしても食べたい",True,(255,255,255)),(btn_choice1.x+70,btn_choice1.y+12))
            screen.blit(font.render("わかった",True,(255,255,255)),(btn_choice2.x+110,btn_choice2.y+12))

        elif scene == "BLUE_ORDER_CHOICE":
            screen.fill((20, 20, 30))

            # ① ボタン1（いらないです）の枠と描画
            btn_choice1 = pygame.Rect(200, 250, 400, 50)  # ※座標・サイズはお好みに調整
            pygame.draw.rect(screen, (60, 60, 120), btn_choice1, border_radius=6)
            screen.blit(font.render("いらないです", True, (255, 255, 255)), (btn_choice1.x + 95, btn_choice1.y + 12))

            # ② 【重要】ボタン2（全部ください）の枠はタイマーの外で「常に作成」しておく！
            btn_choice2 = pygame.Rect(200, 350, 400, 50)  # ※ボタン1の下などに配置

            # ③ 10秒経過したら「描画」だけを行う！
            if blue_order_timer >= 10.0:
                pygame.draw.rect(screen, (120, 60, 60), btn_choice2, border_radius=6)
                screen.blit(font.render("全部ください", True, (255, 255, 255)), (btn_choice2.x + 95, btn_choice2.y + 12))



        elif scene == "WHITE_CHOICE":
            screen.fill((40,40,40))
            btn_choice1 = pygame.Rect(200, 250, 400, 50)  # 座標とサイズはご自身の画面に合わせて調整
            btn_choice2 = pygame.Rect(200, 330, 400, 50)
            
            pygame.draw.rect(screen,(180,180,180),btn_choice1,border_radius=6)
            pygame.draw.rect(screen,(80,80,80),btn_choice2,border_radius=6)
            screen.blit(font.render("一緒に帰りませんか",True,(0,0,0)),(btn_choice1.x+70,btn_choice1.y+12))
            screen.blit(font.render("あなたに気に入られたくないです",True,(255,255,255)),(btn_choice2.x+35,btn_choice2.y+12))

        
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)  # 非同期処理のために追加

    pygame.quit()
    sys.exit()

    if __name__ == "__main__":
        asyncio.run(main())