import math
import os
import random
import sys
import time
import pygame as pg


WIDTH = 1600  # ゲームウィンドウの幅
HEIGHT = 900  # ゲームウィンドウの高さ
NUM_OF_BOMBS = 5 # 爆弾の数
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとんRect，または，爆弾Rect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.right < 0 or WIDTH < obj_rct.left:
        yoko = False
    if obj_rct.bottom < 0 or HEIGHT < obj_rct.top:
        tate = False
    return yoko, tate


class Bird:
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -5),
        pg.K_DOWN: (0, +5),
        pg.K_LEFT: (-5, 0),
        pg.K_RIGHT: (+5, 0),
    }
    img0 = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 2.0)
    img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん（右向き）
    imgs = {  # 0度から反時計回りに定義
        (+5, 0): img,  # 右
        (+5, -5): pg.transform.rotozoom(img, 45, 1.0),  # 右上
        (0, -5): pg.transform.rotozoom(img, 90, 1.0),  # 上
        (-5, -5): pg.transform.rotozoom(img0, -45, 1.0),  # 左上
        (-5, 0): img0,  # 左
        (-5, +5): pg.transform.rotozoom(img0, 45, 1.0),  # 左下
        (0, +5): pg.transform.rotozoom(img, -90, 1.0),  # 下
        (+5, +5): pg.transform.rotozoom(img, -45, 1.0),  # 右下
    }

    def __init__(self, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数 xy：こうかとん画像の初期位置座標タプル
        """
        self.img = __class__.imgs[(+5, 0)]
        self.rct: pg.Rect = self.img.get_rect()
        self.rct.center = xy
        self.dire = (+5, 0)

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.img = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 2.0)
        screen.blit(self.img, self.rct)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rct.move_ip(sum_mv)
        if check_bound(self.rct) != (True, True):
            self.rct.move_ip(-sum_mv[0], -sum_mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.img = __class__.imgs[tuple(sum_mv)]
            self.dire = sum_mv
        screen.blit(self.img, self.rct)


class Bomb:
    """
    爆弾に関するクラス
    """
    def __init__(self, color: tuple[int, int, int], rad: int):
        """
        引数に基づき爆弾円Surfaceを生成する
        引数1 color：爆弾円の色タプル
        引数2 rad：爆弾円の半径
        """
        self.img = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self.img, color, (rad, rad), rad)
        self.img.set_colorkey((0, 0, 0))
        self.rct = self.img.get_rect()
        self.rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self.vx, self.vy = +5, +5

    def update(self, screen: pg.Surface):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        yoko, tate = check_bound(self.rct)
        if not yoko:
            self.vx *= -1
        if not tate:
            self.vy *= -1
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)


class Beam:
    """
    
    """
    def __init__(self, bird: Bird):
        """
        
        """
        self.img = pg.transform.rotozoom(pg.image.load("fig/beam.png"), 0, 2.0) # ビーム画像Surface
        self.vx, self.vy = bird.dire # 縦横速度
        self.rad = math.atan2(-self.vy, self.vx)
        self.img = pg.transform.rotozoom(self.img, math.degrees(self.rad), 2.0)
        self.rct: pg.Rect = self.img.get_rect() # ビーム画像Rect
        BEAM_DELTA = {  # 0度から反時計回りに定義
            (+5, 0): [("left", "centery"), ("right", "centery")],  # 右
            (+5, -5): [("left", "bottom"), ("right", "top")],  # 右上
            (0, -5): [("centerx", "bottom"), ("centerx", "top")],  # 上
            (-5, -5): [("right", "bottom"), ("left", "top")],  # 左上
            (-5, 0): [("right", "centery"), ("left", "centery")],  # 左
            (-5, +5): [("right", "top"), ("left", "bottom")],  # 左下
            (0, +5): [("centerx", "top"), ("centerx", "bottom")],  # 下
            (+5, +5): [("left", "top"), ("right", "bottom")],  # 右下
        }
        setattr(self.rct, BEAM_DELTA[(self.vx, self.vy)][0][0], getattr(bird.rct, BEAM_DELTA[(self.vx, self.vy)][1][0]))
        setattr(self.rct, BEAM_DELTA[(self.vx, self.vy)][0][1], getattr(bird.rct, BEAM_DELTA[(self.vx, self.vy)][1][1]))


    def update(self, screen: pg.Surface):
        """
        
        """
        if check_bound(self.rct) == (True, True):
            self.rct.move_ip(self.vx, self.vy)
            screen.blit(self.img, self.rct)


class Explosion:
    """
    
    """
    def __init__(self, bomb: Bomb):
        """
        
        """
        self.img = [pg.transform.flip(pg.image.load("fig/explosion.gif"), _, _) for _ in [False, True]] # 爆発画像surface
        self.rct: pg.Rect = self.img[0].get_rect() # 爆発画像Rect
        self.rct.center = bomb.rct.center
        self.life = 60

    def update(self, screen: pg.Surface):
        """
        
        """
        if self.life%20 < 10:
            screen.blit(self.img[0], self.rct)
        else:
            screen.blit(self.img[1], self.rct)
        self.life -= 1


class Score:
    def __init__(self):
        self.text = "スコア："
        self.fonto = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 30)
        self.color = (0, 0, 255)
        self.score = 0
        self.img = self.fonto.render(self.text + str(self.score), 0, self.color)
        self.rct = self.img.get_rect()
        self.rct.center = (100, HEIGHT-50)

    def update(self, screen: pg.Surface):
        self.img = self.fonto.render(self.text + str(self.score), 0, self.color)
        screen.blit(self.img, self.rct)

def main():
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))    
    bg_img = pg.image.load("fig/pg_bg.jpg")
    bird = Bird((900, 400))
    bombs = [Bomb((255, 0, 0), 10) for _ in range(NUM_OF_BOMBS)]
    explosions = []
    beams = []
    explosion = None
    score = Score()
    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                beams .append(Beam(bird))


        screen.blit(bg_img, [0, 0])
        
        for bomb in bombs:
            if bird.rct.colliderect(bomb.rct):
                # ゲームオーバー時に，こうかとん画像を切り替え，1秒間表示させる
                bird.change_img(8, screen)
                fonto = pg.font.Font(None, 80)
                txt = fonto.render("Game Over", True, (255, 0, 0))
                screen.blit(txt, [WIDTH/2-150, HEIGHT/2])
                pg.display.update()
                time.sleep(2)
                return
        
        
        for i, bomb in enumerate(bombs):
            if len(beams) > 0:
                for j, beam in enumerate(beams):
                    if beam is not None and beam.rct.colliderect(bomb.rct): # ビームと爆弾が衝突した場合
                        beams[j] = None
                        bombs[i] = None
                        bird.change_img(6, screen)
                        explosions.append(Explosion(bomb))
                        score.score += 1
                        pg.display.update()
                    if beam is not None and any((beam.rct.centerx < 0, beam.rct.centerx > WIDTH, beam.rct.centery < 0, beam.rct.centery > HEIGHT)):
                        beams[i] = None
        bombs = [bomb for bomb in bombs if bomb is not None]
        beams = [beam for beam in beams if beam is not None]
        explosions = [explosion for explosion in explosions if explosion.life >= 0]
        for explosion in explosions:
            explosion.update(screen)

        score.update(screen)
        
        if len(bombs) == 0:
            bird.change_img(6, screen)
            fonto = pg.font.Font(None, 80)
            txt = fonto.render("Game Clear", True, (255, 255, 0))
            screen.blit(txt, [WIDTH/2-150, HEIGHT/2])
            pg.display.update()
            time.sleep(2)
            return

        key_lst = pg.key.get_pressed()
        bird.update(key_lst, screen)
        
        for bomb in bombs:
            bomb.update(screen)
        if len(beams) > 0:
            for beam in beams:
                beam.update(screen)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
