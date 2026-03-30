import math
import os
import random
import struct
import sys
import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import pygame


GAME_NAME_CN = "开开你的！"
GAME_NAME_EN = "Gotcha !"

BOARD_SIZE = 9
BASE_CELL_SIZE = 68
BASE_BOARD_MARGIN = 24
BASE_PANEL_WIDTH = 430

CELL_SIZE = BASE_CELL_SIZE
BOARD_MARGIN = BASE_BOARD_MARGIN
PANEL_WIDTH = BASE_PANEL_WIDTH
WINDOW_WIDTH = BOARD_MARGIN * 2 + BOARD_SIZE * CELL_SIZE + PANEL_WIDTH
WINDOW_HEIGHT = BOARD_MARGIN * 2 + BOARD_SIZE * CELL_SIZE

FPS = 90
TEXT_COLOR = (244, 248, 255)
SUB_TEXT = (177, 190, 218)
BG_COLOR = (18, 22, 33)
BOARD_BG = (29, 37, 57)
GRID_COLOR = (72, 94, 138)
HIGHLIGHT = (255, 214, 128)
DISABLED_TEXT = (108, 116, 136)

PLAYER_COLORS = [
    (242, 86, 86),
    (246, 198, 63),
    (82, 206, 115),
    (81, 163, 245),
]

MODE_NORMAL = 0
MODE_ADV1 = 1
MODE_ADV2 = 2
MODE_ADV3 = 3
MODE_ADV4 = 4

MODE_NAMES = {
    MODE_NORMAL: "普通",
    MODE_ADV1: "进阶 1",
    MODE_ADV2: "进阶 2",
    MODE_ADV3: "暗黑心理学",
    MODE_ADV4: "牛顿摆",
}

MODE_NAMES_EN = {
    MODE_NORMAL: "Standard",
    MODE_ADV1: "Advanced 1",
    MODE_ADV2: "Advanced 2",
    MODE_ADV3: "Advanced 3",
    MODE_ADV4: "Advanced 4",
}

TIME_MIN = 5
TIME_MAX = 60
TIME_DEFAULT = 30
FIRST_ROUND_FIXED_SYMBOL = "O"

RULES_TEXT = [
    "开开你的！/ Gotcha ! 游戏规则",
    "",
    "",
    "1. 基础设定",
    "",
    "· 9 × 9 棋盘，4 名玩家随机分为「圈（O）」或「叉（X）」阵营，每阵营 2 人，玩家之间互不知晓阵营；",
    "",
    "· 每人从「红、黄、绿、蓝」四种颜色种选择一种，使棋子通过颜色与玩家绑定；",
    "",
    "· 将四种颜色随机排序为 P1 ~ P4，按顺序轮流落子。",
    "",
    "",
    "2. 落子规则",
    "",
    "轮到自己时，可选择落 O，也可选择落 X，不可悔棋。你将有 30 秒的时间，谨言慎行吧！",
    "",
    "* 倒计时结束后若未落棋则自动跳过（标 * 号的项表示这可能会影响该游戏原本的乐趣，我们不建议这样做，如果有玩家执意这样做，我们建议不要和这些玩家玩该游戏）。",
    "",
    "",
    "3. 开盒规则",
    "",
    "· 就是你！- 开盒成功：在一条有效四连（有效四连：由一种或两种颜色的棋子构成的「同符号」、横 / 纵 / 斜向的四枚连续棋子）中，所有颜色均属于「发起开盒的玩家一方的阵营」，致使「发起开盒的玩家」的阵营获胜。此种结局会在任意模式出现；",
    "",
    "· 你居然！- 开盒失败 / 诱导开盒成功：在一条由两种颜色构成的有效四连中，另一种颜色不属于「发起开盒的玩家一方的阵营」，致使「发起开盒的玩家」的阵营失败，另一阵营获胜。此种结局会在任意模式出现；",
    "",
    "· 得吃了！- 诱导开盒成功：在两步验证中，后者的同意致使「发起开盒的玩家」的阵营获胜，而「同意开盒的玩家」的阵营失败。此种结局会在进阶 2 及以上模式出现；",
    "",
    "* 你干嘛哈哈哎哟 - 单人送赢：一名玩家通过仅落对方阵营的棋子构成一条有效四连并开盒，致使对方阵营获胜。此种结局仅在普通模式出现；",
    "",
    "* 你俩干嘛哈哈哎哟 - 双人送赢：两名玩家通过仅落对方阵营的棋子构成一条有效四连并开盒，致使对方阵营获胜。此种结局会在任意模式出现。",
    "",
    "当玩家本次落子，新构成了有效四连时，可选择开盒。若选择开盒，则该玩家的倒计时暂停，全员揭示阵营，宣布获胜阵营，游戏结束。若选择不开盒或倒计时结束，则该有效四连作废，游戏继续。",
    "",
    "",
    "4. 多条有效四连规则",
    "",
    "一次落子构成多条有效四连的，若玩家选择开盒，仅可选择其中一条。",
    "",
    "",
    "5. 边界规则",
    "",
    "当棋盘下满时，和棋并揭示阵营。",
    "",
    "",
    "6. 进阶模式",
    "",
    "· 进阶 1 - 单飞禁止：由一种颜色的棋子构成的四连不再被视为有效四连。",
    "",
    "· 进阶 2 - 两步验证：一名玩家发起开盒后，构成有效四连的另一玩家也需要同意才能开盒。若后者同意，前者不能反悔。若后者不同意，则该有效四连作废，游戏继续；以及之前的进阶修改。",
    "",
    "· 进阶 3 - 暗黑心理学：所有玩家第一回合（回合：从游戏开始算起，到所有玩家均落子一枚为止，称为第一回合，以此类推）只能落 O（或者 X，可自行修改）；以及之前的进阶修改。",
    "",
    "· 进阶 4 - 牛顿摆：每轮回合玩家顺序转向，即：P1 → P2 → P3 → P4 → P4 → P3 → P2 → P1 → P1 → P2 → …… 以此类推；以及之前的进阶修改。",
    "",
    "进阶模式仅能选择其中一个。",
    "",
    "",
    "7. 自定义选项",
    "",
    "· 转人工：禁用聊天框。",
    "",
    "· 请输入文本：禁用麦克风。",
    "",
    "· 已严肃下棋：禁用聊天框和麦克风。",
    "",
    "· 经典开局：一局游戏的第一枚棋子只能落在棋盘中央。",
    "",
    "· 正弦波：所有玩家的落子符号必须交替，即：如果一名玩家本回合落了 O，那么这名玩家下一回合只能落 X。",
    "",
    "· 时间吞噬者：调整每名玩家的可用时间（5 ~ 60 秒）。",
    "",
    "自定义选项可以同时开启多个，开启后对任意模式均生效。",
]

RULES_TEXT_EN = [
    "开开你的！/ Gotcha ! Game Rules",
    "",
    "",
    "1. Basic Setup",
    "",
    "· A 9 × 9 board ; Four players are randomly assigned to either the ' O ' or ' X ' team , with 2 players per team ; players do not know each other's team ;",
    "",
    "· Each player chooses one of the four colours ( red , yellow , green or blue ) , so that the pieces are bonded to the player by colour ;",
    "",
    "· The 4 colours are randomly assigned as P1 ~ P4 , and players take turns placing their pieces in that order .",
    "",
    "",
    "2. Placement Rules",
    "",
    "When it is your turn , you may choose to place an O or an X ; moves cannot be withdrawn . You will have 30 seconds - so think carefully !",
    "",
    "* If a player has not placed a piece by the end of the countdown , their round is automatically skipped ( Items marked with an asterisk ( * ) may detract from the game's original enjoyment ; we do not recommend doing so . If any player( s ) insist on doing so , we advise against playing the game with them ) .",
    "",
    "",
    "3. Box - opening Rules",
    "",
    "· I knew it ! ( successful box - opening ) : In a VFR ( Valid Four-in-a-Row , four consecutive pieces of the same mark consisting of 1 or 2 colours arranged horizontally , vertically or diagonally ) , all colour( s ) belong( s ) to the team of the player who initiated the box - opening , resulting in the winning of the team of the player who initiated the box - opening . This outcome can occur in any mode ;",
    "",
    "· Liar ! ( unsuccessful box - opening / successful induced box - opening ) : In a VFR consisting of 2 colours , the other colour does not belong to the team of the initiator of the box - opening , resulting in the losing of the team of the initiator of the box - opening , and the winning of the opposing team . This outcome can occur in any mode ;",
    "",
    "· Gotcha ! ( successful induced box - opening ) : In a 2FA ( 2 - Factor Agreement ) , the latter one's agreement results in the winning of the team of the team of the initiator of the box - opening , and the losing of the team of the player who agrees to ' open the box ' . This outcome occurs in Advanced 2 & 2+ modes ;",
    "",
    "* Quoi t'fais ? ( Solo throwing ) : A player forms a VFR using only marks of the opposing team and ' opens the box ' , resulting in the winning of the opposing team . This outcome occurs only in standard mode ;",
    "",
    "* Quoi vous faites ? ( Duo throwing ) : Two players form a VFR using only marks of the opposing team and one ' opens the box ' , resulting in the winning of the opposing team . This outcome can occur in any mode .",
    "",
    "When a player makes a move that forms a new VFR , they may choose to ' open the box ' . If they choose to do so , their countdown is paused , all players reveal their belonging team , the winning team is presented , and the game ends . If they choose not to ' open the box ' or their available time expires , the VFR is void and the game continues .",
    "",
    "",
    "4. Multiple VFRs Rule",
    "",
    "If a single move forms multiple lines of VFR , the player may only select one of them to ' open the box ' .",
    "",
    "",
    "5. Boundary Rule",
    "",
    "When the board is full , the game ends in a draw and all players reveal their belonging team .",
    "",
    "",
    "6. Advanced Modes",
    "",
    "· Advanced 1 - Solo VFR Banned : A four-in-a-row formed by a single colour is no longer treated as a VFR .",
    "",
    "· Advanced 2 - 2FA : After one player initiates a box - opening , it is required that the other player involved in the VFR also agree to ' open the box ' . If the latter agrees , the former cannot change their mind . If the latter disagrees , that VFR is void and the game continues ; and the previous modifications .",
    "",
    "· Advanced 3 - Masquerade : In the 1st round ( the 1st round is defined as the period from the start of the game until all players have placed one piece each , the 2nd round by analogy and so on ) , all players may only place an O ( or an X , which may be modified at the players' discretion ) ; and the previous modifications .",
    "",
    "· Advanced 4 - Newton's Pendulum : The player order makes a U - turn each round ; that is , P1 → P2 → P3 → P4 → P4 → P3 → P2 → P1 → P1 → P2 → … and so on ; and the previous modifications .",
    "",
    "Only one advanced mode may be selected .",
    "",
    "",
    "7. Custom Options",
    "",
    "· Speaking is fun ! : All chat boxes are disabled .",
    "",
    "· Typing is fun ! : All microphones are disabled .",
    "",
    "· Muting is fun ( Probably ? ) : Both chat boxes and microphones are disabled .",
    "",
    "· Classic Start : The first piece of a game must be placed in the centre of the board .",
    "",
    "· Sine Wave : All players' marks must alternate each round ; that is , if a player places an O this round , they must place an X on the next round .",
    "",
    "· Time Eater : Adjust the available time for each player ( 5 ~ 60 seconds ) .",
    "",
    "Multiple options can be enabled simultaneously and they apply to all modes .",
]

MODE_HOVER_RULES = {
    MODE_ADV1: "由一种颜色的棋子构成的四连不再被视为有效四连。",
    MODE_ADV2: "一名玩家发起开盒后，构成有效四连的另一玩家也需要同意才能开盒。若后者同意，前者不能反悔。若后者不同意，则该有效四连作废，游戏继续；以及之前的进阶修改。",
    MODE_ADV3: "所有玩家第一回合（回合：从游戏开始算起，到所有玩家均落子一枚为止，称为第一回合，以此类推）只能落 O（或者 X，可自行修改）；以及之前的进阶修改。",
    MODE_ADV4: "每轮回合玩家顺序转向，即：P1 → P2 → P3 → P4 → P4 → P3 → P2 → P1 → P1 → P2 → …… 以此类推；以及之前的进阶修改。",
}

MODE_HOVER_RULES_EN = {
    MODE_ADV1: "A four-in-a-row formed by a single colour is no longer treated as a VFR.",
    MODE_ADV2: "After one player initiates a box-opening, the other player involved in the VFR must also agree. If they agree, the initiator cannot regret it. If they reject, the VFR is void; previous advanced changes still apply.",
    MODE_ADV3: "In round 1, all players may only place O (or X, configurable); previous advanced changes still apply.",
    MODE_ADV4: "Turn order makes a U-turn each round: P1 → P2 → P3 → P4 → P4 → P3 → P2 → P1 → P1 → P2 → ... ; previous advanced changes still apply.",
}

OPTION_HOVER_RULES = {
    1: "禁用聊天框。",
    2: "禁用麦克风。",
    3: "禁用聊天框和麦克风。",
    4: "一局游戏的第一枚棋子只能落在棋盘中央。",
    5: "所有玩家的落子符号必须交替，即：如果一名玩家本回合落了 O，那么这名玩家下一回合只能落 X。",
    6: "时间吞噬者：调整每名玩家的可用时间（5 ~ 60 秒）。",
}

OPTION_HOVER_RULES_EN = {
    1: "All chat boxes are disabled.",
    2: "All microphones are disabled.",
    3: "Both chat boxes and microphones are disabled.",
    4: "The first piece of a game must be placed in the center of the board.",
    5: "All players' marks must alternate each round.",
    6: "Time Eater: adjust the available time for each player (5 ~ 60 seconds).",
}


def load_zh_font(size: int) -> pygame.font.Font:
    candidates = [
        r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\simhei.ttf",
        r"C:\Windows\Fonts\simsun.ttc",
        r".\assets\fonts\NotoSansSC-Regular.otf",
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                return pygame.font.Font(p, size)
            except Exception:
                pass
    return pygame.font.Font(None, size)


@dataclass
class Player:
    pid: int
    color: Tuple[int, int, int]
    camp: str


@dataclass
class Piece:
    symbol: str
    owner_pid: int


@dataclass
class PendingPiece:
    row: int
    col: int
    symbol: str
    owner_pid: int


@dataclass
class LineCandidate:
    symbol: str
    cells: List[Tuple[int, int]]
    direction: str


@dataclass
class FeedbackEntry:
    text: str
    color: Tuple[int, int, int] = SUB_TEXT
    bold: bool = False
    separator: bool = False
    player_pid: Optional[int] = None


class AppState:
    HOME = "home"
    MODE_MENU = "mode_menu"
    OPTION_MENU = "option_menu"
    REVEAL = "reveal"
    GAME = "game"
    CREDITS = "credits"


class Gotcha:
    def _enable_dpi_awareness(self):
        if os.name != "nt":
            return
        try:
            import ctypes
            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(2)
            except Exception:
                ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

    def _get_dpi_scale(self) -> float:
        if os.name != "nt":
            return 1.0
        try:
            import ctypes
            try:
                dpi = ctypes.windll.user32.GetDpiForSystem()
                if dpi and dpi > 0:
                    return max(1.0, dpi / 96.0)
            except Exception:
                pass

            try:
                hdc = ctypes.windll.user32.GetDC(0)
                LOGPIXELSX = 88
                dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, LOGPIXELSX)
                ctypes.windll.user32.ReleaseDC(0, hdc)
                if dpi and dpi > 0:
                    return max(1.0, dpi / 96.0)
            except Exception:
                pass
        except Exception:
            pass
        return 1.0

    def _configure_layout(self):
        global CELL_SIZE, BOARD_MARGIN, PANEL_WIDTH, WINDOW_WIDTH, WINDOW_HEIGHT
        base_w = BASE_BOARD_MARGIN * 2 + BOARD_SIZE * BASE_CELL_SIZE + BASE_PANEL_WIDTH
        base_h = BASE_BOARD_MARGIN * 2 + BOARD_SIZE * BASE_CELL_SIZE

        dpi_scale = self._get_dpi_scale()
        s = dpi_scale

        info = pygame.display.Info()
        max_w = max(900, info.current_w - 40)
        max_h = max(640, info.current_h - 80)
        target_w = base_w * s
        target_h = base_h * s
        fit = min(1.0, max_w / target_w if target_w > 0 else 1.0, max_h / target_h if target_h > 0 else 1.0)
        s *= fit

        CELL_SIZE = max(62, int(round(BASE_CELL_SIZE * s)))
        BOARD_MARGIN = max(20, int(round(BASE_BOARD_MARGIN * s)))
        PANEL_WIDTH = max(430, int(round(BASE_PANEL_WIDTH * s)))
        WINDOW_WIDTH = BOARD_MARGIN * 2 + BOARD_SIZE * CELL_SIZE + PANEL_WIDTH
        WINDOW_HEIGHT = BOARD_MARGIN * 2 + BOARD_SIZE * CELL_SIZE
        self.ui_scale = s

    def __init__(self):
        self._enable_dpi_awareness()
        pygame.mixer.pre_init(48000, -16, 2, 128)
        pygame.init()
        self._configure_layout()
        self.audio_ready = False
        self.sfx: Dict[str, pygame.mixer.Sound] = {}
        self._last_tick_sfx_time = 0
        try:
            pygame.mixer.init()
            pygame.mixer.set_num_channels(16)
            self.audio_ready = True
        except Exception:
            self.audio_ready = False

        pygame.display.set_caption(f"{GAME_NAME_CN} / {GAME_NAME_EN}")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()

        def fs(px: int) -> int:
            return max(12, int(round(px * self.ui_scale)))

        self.font = load_zh_font(fs(25))
        self.font_bold = load_zh_font(fs(25))
        self.font_bold.set_bold(True)
        self.font_mid = load_zh_font(fs(21))
        self.font_mid_bold = load_zh_font(fs(21))
        self.font_mid_bold.set_bold(True)
        self.font_small = load_zh_font(fs(17))
        self.font_small_italic = load_zh_font(fs(17))
        self.font_small_italic.set_italic(True)
        self.font_small_italic_bold = load_zh_font(fs(17))
        self.font_small_italic_bold.set_italic(True)
        self.font_small_italic_bold.set_bold(True)
        self.font_rule = load_zh_font(fs(16))
        self.font_rule_bold = load_zh_font(fs(16))
        self.font_rule_bold.set_bold(True)
        self.font_rule_italic = load_zh_font(fs(16))
        self.font_rule_italic.set_italic(True)

        self.board_x = BOARD_MARGIN
        self.board_y = BOARD_MARGIN
        self.panel_x = self.board_x + BOARD_SIZE * CELL_SIZE + 20

        self.app_state = AppState.HOME
        self.show_rules = False
        self.rules_page = 0

        self.mode = MODE_NORMAL
        self.english_mode = False

        self.option_disable_chat = False
        self.option_disable_mic = False
        self.option_disable_both = False
        self.option_center_first = False
        self.option_symbol_alternate = False
        self.turn_time_limit = TIME_DEFAULT
        self.turn_time_limit_visual = float(TIME_DEFAULT)

        self.first_round_symbol_choice = FIRST_ROUND_FIXED_SYMBOL
        self.btn_adv3_o = pygame.Rect(0, 0, 0, 0)
        self.btn_adv3_x = pygame.Rect(0, 0, 0, 0)

        self.players: List[Player] = []
        self.turn_order: List[Player] = []
        self.turn_index = 0
        self.turn_dir = 1
        self.turn_step = 0
        self.player_last_symbol: Dict[int, Optional[str]] = {}

        self.board: List[List[Optional[Piece]]] = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.pending_piece: Optional[PendingPiece] = None
        self.pending_lines: List[LineCandidate] = []
        self.last_confirmed_cell: Optional[Tuple[int, int]] = None
        self.selected_symbol = "O"

        self.turn_time_left = float(self.turn_time_limit)
        self.touched_this_turn = False
        self.open_waiting_consent = False
        self.consent_player_pid: Optional[int] = None
        self.chosen_line: Optional[LineCandidate] = None
        self.hover_open_line_idx: Optional[int] = None
        self.hover_open_line_draw_idx: Optional[int] = None
        self.hover_open_line_alpha = 0.0
        self.opened_line_cells: Optional[List[Tuple[int, int]]] = None
        self.waiting_line_cells: Optional[List[Tuple[int, int]]] = None
        self.rejected_line_cells: Optional[List[Tuple[int, int]]] = None
        self.rejected_line_alpha = 0.0
        self.consent_status_text: str = ""

        self.reveal_hold_pid: Optional[int] = None
        self.reveal_viewed: set[int] = set()
        self.left_mouse_down = False

        self.game_over = False
        self.winner_text = ""

        self.feedback: List[FeedbackEntry] = []
        self.feedback_scroll_target = 0.0
        self.feedback_scroll_display = 0.0
        self.feedback_thumb_rect = pygame.Rect(0, 0, 0, 0)
        self.feedback_dragging = False
        self.feedback_drag_offset = 0
        self.action_scroll_target = 0.0
        self.action_scroll_display = 0.0
        self.action_thumb_rect = pygame.Rect(0, 0, 0, 0)
        self.action_dragging = False
        self.action_drag_offset = 0

        self.ui_transition_alpha = 0.0
        self._last_app_state = self.app_state
        self._last_show_rules = self.show_rules
        self.reveal_hint_alpha = 0.0
        self.credits_return_state = AppState.HOME
        self.readonly_shake_elapsed = 999.0
        self.readonly_shake_duration = 0.42
        self.pressed_button_rect: Optional[pygame.Rect] = None
        self.checkbox_bounce_elapsed: Dict[int, float] = {1: 999.0, 2: 999.0, 3: 999.0, 4: 999.0, 5: 999.0}
        self.checkbox_bounce_duration = 0.38
        self.button_hover_scale: Dict[str, float] = {}
        self.checkbox_hover_scale: Dict[int, float] = {1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0, 5: 1.0}
        self.disabled_button_shake_elapsed: Dict[str, float] = {}
        self.disabled_button_shake_duration = 0.42
        self.adv3_label_shift = 0.0
        self.rules_overlay_alpha = 0.0
        self.hover_hint_alpha = 0.0
        self.hover_hint_text = ""
        self._rules_wrap_width_cached = -1
        self._rules_lines_cached: List[Tuple[str, bool]] = []
        self._rules_pages_height_cached = -1
        self._rules_pages_cached: List[List[Tuple[str, bool]]] = []
        self._rules_page_surface_key: Optional[Tuple[int, int, int]] = None
        self._rules_page_surfaces: List[pygame.Surface] = []
        self.rules_page_display = 0.0

        self._init_audio()
        self._init_ui()

    # ---------- 格式辅助 ----------
    def _t(self, zh: str, en: str) -> str:
        return en if self.english_mode else zh

    def _u(self, v: int) -> int:
        return int(round(v * self.ui_scale))

    def _pn(self, pid: int) -> str:
        return f"P{pid}" if self.english_mode else f"玩家 {pid}"

    def _coord(self, row: int, col: int) -> str:
        return f"( {col + 1}x, {row + 1}y )"

    def _check_char(self, checked: bool) -> str:
        return "☑" if checked else "☐"

    def _mode_desc(self) -> str:
        if self.mode == MODE_NORMAL:
            return self._t("普通", "Standard")
        if self.mode == MODE_ADV1:
            return self._t("进阶 1 - 单飞禁止", "Advanced 1 - Solo VFR Banned")
        if self.mode == MODE_ADV2:
            return self._t("进阶 2 - 两步验证、单飞禁止", "Advanced 2 - 2FA, Solo VFR Banned")
        if self.mode == MODE_ADV3:
            return self._t(
                f"进阶 3 - 暗黑心理学 ({self.first_round_symbol_choice})、两步验证、单飞禁止",
                f"Advanced 3 - Masquerade ({self.first_round_symbol_choice}), 2FA, Solo VFR Banned",
            )
        return self._t(
            f"进阶 4 - 牛顿摆、假面舞会 ({self.first_round_symbol_choice})、两步验证、单飞禁止",
            f"Advanced 4 - Newton's Pendulum, Masquerade ({self.first_round_symbol_choice}), 2FA, Solo VFR Banned",
        )

    def _mode_short(self) -> str:
        if self.mode == MODE_NORMAL:
            return self._t("普通", "Standard")
        return f"Advanced {self.mode}" if self.english_mode else f"进阶 {self.mode}"

    def _layout_game_panel_controls(self):
        u = self._u
        oy = u(56)
        multiline_mode_desc = self.mode == MODE_ADV4 or (self.english_mode and self.mode == MODE_ADV3)
        time_y = oy + (u(44) if multiline_mode_desc else u(22))
        row_base = time_y + u(34)

        symbol_y = row_base + u(52)
        self.btn_symbol_o.y = symbol_y
        self.btn_symbol_x.y = symbol_y

        self.action_area_y = self.btn_symbol_o.bottom + u(10)

    def _mode_menu_label(self, mode: int) -> str:
        if not self.english_mode:
            return {
                MODE_NORMAL: "普通",
                MODE_ADV1: "进阶 1 - 单飞禁止",
                MODE_ADV2: "进阶 2 - 两步验证",
                MODE_ADV3: "进阶 3 - 暗黑心理学",
                MODE_ADV4: "进阶 4 - 牛顿摆",
            }[mode]
        return {
            MODE_NORMAL: "Standard",
            MODE_ADV1: "Advanced 1 - Solo VFR Banned",
            MODE_ADV2: "Advanced 2 - 2FA",
            MODE_ADV3: "Advanced 3 - Masquerade",
            MODE_ADV4: "Advanced 4 - Newton's Pendulum",
        }[mode]

    def _init_audio(self):
        if not self.audio_ready:
            return

        def load(paths: List[str]) -> Optional[pygame.mixer.Sound]:
            for p in paths:
                if os.path.exists(p):
                    try:
                        return pygame.mixer.Sound(p)
                    except Exception:
                        pass
            return None

        click = load([
            r".\assets\sfx\button_click.wav",
            r".\assets\sfx\click.wav",
        ])
        check = load([
            r".\assets\sfx\checkbox.wav",
            r".\assets\sfx\check.wav",
        ])
        tick = load([
            r".\assets\sfx\tick.wav",
            r".\assets\sfx\ratchet.wav",
        ])
        place = load([
            r".\assets\sfx\place.wav",
            r".\assets\sfx\drop.wav",
        ])
        confirm = load([
            r".\assets\sfx\confirm.wav",
            r".\assets\sfx\commit.wav",
        ])

        if click:
            self.sfx["click"] = click
        if check:
            self.sfx["check"] = check
        if tick:
            self.sfx["tick"] = tick
        if place:
            self.sfx["place"] = place
        if confirm:
            self.sfx["confirm"] = confirm

        if "click" not in self.sfx or "check" not in self.sfx or "tick" not in self.sfx or "place" not in self.sfx or "confirm" not in self.sfx:
            init_info = pygame.mixer.get_init()
            if init_info is not None:
                sample_rate, _, channels = init_info

                def make_tone(freq: float, ms: int, vol: float = 0.32, decay: float = 8.0) -> pygame.mixer.Sound:
                    n = max(1, int(sample_rate * (ms / 1000.0)))
                    buf = bytearray()
                    for i in range(n):
                        t = i / sample_rate
                        env = math.exp(-decay * t)
                        v = int(32767 * vol * env * math.sin(2.0 * math.pi * freq * t))
                        packed = struct.pack("<h", max(-32768, min(32767, v)))
                        if channels >= 2:
                            buf.extend(packed)
                            buf.extend(packed)
                        else:
                            buf.extend(packed)
                    return pygame.mixer.Sound(buffer=bytes(buf))

                if "click" not in self.sfx:
                    self.sfx["click"] = make_tone(880, 65, 0.28, 14.0)
                if "check" not in self.sfx:
                    self.sfx["check"] = make_tone(1040, 75, 0.30, 12.0)
                if "tick" not in self.sfx:
                    self.sfx["tick"] = make_tone(520, 45, 0.22, 18.0)
                if "place" not in self.sfx:
                    self.sfx["place"] = make_tone(420, 80, 0.30, 9.0)
                if "confirm" not in self.sfx:
                    self.sfx["confirm"] = make_tone(660, 95, 0.34, 7.0)

        for s in self.sfx.values():
            try:
                s.set_volume(0.75)
            except Exception:
                pass

    def _play_sfx(self, key: str, throttle_ms: int = 0):
        if not self.audio_ready:
            return
        s = self.sfx.get(key)
        if s is None:
            return
        if throttle_ms > 0:
            now = pygame.time.get_ticks()
            if now - self._last_tick_sfx_time < throttle_ms:
                return
            self._last_tick_sfx_time = now
        try:
            ch = pygame.mixer.find_channel(True)
            if ch is not None:
                ch.play(s)
            else:
                s.play()
        except Exception:
            pass

    def _sync_disable_options(self):
        self.option_disable_both = self.option_disable_chat and self.option_disable_mic

    def _readonly_shake_offset(self) -> int:
        if self.readonly_shake_elapsed >= self.readonly_shake_duration:
            return 0
        p = self.readonly_shake_elapsed / self.readonly_shake_duration
        amp = 7.0 * (1.0 - p)
        return int(round(math.sin(self.readonly_shake_elapsed * 46.0) * amp))

    def _trigger_readonly_shake(self):
        self.readonly_shake_elapsed = 0.0

    def _checkbox_bounce_offset(self, idx: int) -> int:
        t = self.checkbox_bounce_elapsed.get(idx, 999.0)
        if t >= self.checkbox_bounce_duration:
            return 0
        p = t / self.checkbox_bounce_duration
        amp = 7.0 * (1.0 - p)
        return int(round(math.sin(t * 38.0) * amp))

    def _trigger_checkbox_bounce(self, idx: int):
        self.checkbox_bounce_elapsed[idx] = 0.0

    def _checkbox_hover_scale_value(self, idx: int, hovered: bool) -> float:
        cur = self.checkbox_hover_scale.get(idx, 1.0)
        target = 1.18 if hovered else 1.0
        cur += (target - cur) * 0.28
        self.checkbox_hover_scale[idx] = cur
        return cur

    def _disabled_button_shake_key(self, rect: pygame.Rect) -> str:
        return f"{rect.x},{rect.y},{rect.width},{rect.height}"

    def _trigger_disabled_button_shake(self, rect: pygame.Rect):
        self.disabled_button_shake_elapsed[self._disabled_button_shake_key(rect)] = 0.0

    def _disabled_button_shake_offset(self, rect: pygame.Rect) -> int:
        key = self._disabled_button_shake_key(rect)
        t = self.disabled_button_shake_elapsed.get(key, 999.0)
        if t >= self.disabled_button_shake_duration:
            return 0
        p = t / self.disabled_button_shake_duration
        amp = 7.0 * (1.0 - p)
        return int(round(math.sin(t * 44.0) * amp))

    def _handle_readonly_checkbox_click(self, mx: int, my: int) -> bool:
        u = self._u
        if self.app_state == AppState.HOME:
            x = self.panel_x + u(20)
            sy = u(152)
            areas = [
                pygame.Rect(x, sy + u(54), u(166), u(22)),
                pygame.Rect(x + u(188), sy + u(54), u(166), u(22)),
                pygame.Rect(x, sy + u(78), u(166), u(22)),
                pygame.Rect(x + u(188), sy + u(78), u(166), u(22)),
            ]
        elif self.app_state == AppState.GAME:
            x = self.panel_x + u(16)
            oy = u(56)
            multiline_mode_desc = self.mode == MODE_ADV4 or (self.english_mode and self.mode == MODE_ADV3)
            time_y = oy + (u(44) if multiline_mode_desc else u(22))
            row_base = time_y + u(34)
            areas = [
                pygame.Rect(x, row_base - u(2), u(154), u(22)),
                pygame.Rect(x + u(168), row_base - u(2), u(154), u(22)),
                pygame.Rect(x, row_base + u(20), u(154), u(22)),
                pygame.Rect(x + u(168), row_base + u(20), u(154), u(22)),
            ]
        else:
            return False

        if any(a.collidepoint(mx, my) for a in areas):
            self._trigger_readonly_shake()
            self._play_sfx("check")
            return True
        return False

    def _disabled_button_rects(self) -> List[pygame.Rect]:
        out: List[pygame.Rect] = []

        if self.show_rules:
            u = self._u
            content = pygame.Rect(u(40 + 16), u(30 + 50), WINDOW_WIDTH - u(80 + 32), WINDOW_HEIGHT - u(60 + 100))
            lines = self._wrap_rules_cached(content.width)
            pages = self._paginate_rules_cached(lines, content.height)
            is_first = self.rules_page <= 0
            is_last = self.rules_page >= len(pages) - 1
            if is_first:
                out.append(self.btn_rule_prev)
            if is_last:
                out.append(self.btn_rule_next)
            return out

        if self.app_state == AppState.REVEAL:
            if len(self.reveal_viewed) != 4:
                out.append(self.btn_reveal_start)

        if self.app_state == AppState.GAME and not self.game_over:
            avail = self._available_symbols(self.current_player())
            if "O" not in avail:
                out.append(self.btn_symbol_o)
            if "X" not in avail:
                out.append(self.btn_symbol_x)
            for rect, kind, _ in self._action_buttons():
                if kind == "confirm_disabled":
                    out.append(rect)

        return out

    def _is_text_button_hit(self, mx: int, my: int) -> bool:
        if self.show_rules:
            return (
                self.btn_rule_close.collidepoint(mx, my)
                or self.btn_rule_prev.collidepoint(mx, my)
                or self.btn_rule_next.collidepoint(mx, my)
            )

        if self.btn_q.collidepoint(mx, my):
            return True

        if self.btn_home_credits.collidepoint(mx, my):
            return True

        if self.app_state == AppState.HOME:
            return (
                self.btn_home_start.collidepoint(mx, my)
                or self.btn_home_mode.collidepoint(mx, my)
                or self.btn_home_option.collidepoint(mx, my)
                or self.btn_home_english.collidepoint(mx, my)
            )
        if self.app_state == AppState.MODE_MENU:
            if self.btn_mode_back.collidepoint(mx, my) or self.btn_adv3_o.collidepoint(mx, my) or self.btn_adv3_x.collidepoint(mx, my):
                return True
            return any(rect.collidepoint(mx, my) for rect, _, _ in self.mode_btns)
        if self.app_state == AppState.OPTION_MENU:
            return self.btn_opt_back.collidepoint(mx, my)
        if self.app_state == AppState.REVEAL:
            return self.btn_reveal_start.collidepoint(mx, my) or self.btn_reveal_home.collidepoint(mx, my)
        if self.app_state == AppState.GAME:
            self._layout_game_panel_controls()
            if (
                self.btn_symbol_o.collidepoint(mx, my)
                or self.btn_symbol_x.collidepoint(mx, my)
                or self.btn_restart.collidepoint(mx, my)
                or self.btn_exit_home.collidepoint(mx, my)
            ):
                return True
            items, _, _ = self._action_buttons_view()
            return any(rect.collidepoint(mx, my) for rect, _, _ in items)
        return False

    def _on_text_button_release(self, mx: int, my: int):
        self._play_sfx("click")
        if self.show_rules:
            self._handle_rules_click(mx, my)
            return

        if self.btn_home_credits.collidepoint(mx, my):
            if self.app_state == AppState.CREDITS:
                target = self.credits_return_state
                self.app_state = target if target != AppState.CREDITS else AppState.HOME
            else:
                self.credits_return_state = self.app_state
                self.app_state = AppState.CREDITS
            return

        if self.app_state == AppState.HOME:
            if self.btn_home_english.collidepoint(mx, my):
                self.english_mode = not self.english_mode
                self._rules_wrap_width_cached = -1
                self._rules_pages_height_cached = -1
                self._rules_lines_cached = []
                self._rules_pages_cached = []
                self._rules_page_surface_key = None
                self._rules_page_surfaces = []
                return
            self._handle_home_click(mx, my)
        elif self.app_state == AppState.MODE_MENU:
            self._handle_mode_menu_click(mx, my)
        elif self.app_state == AppState.OPTION_MENU:
            self._handle_option_menu_click(mx, my)
        elif self.app_state == AppState.REVEAL:
            self._handle_reveal_click(mx, my)
        elif self.app_state == AppState.GAME:
            self._handle_game_click(mx, my)
        elif self.app_state == AppState.CREDITS:
            self._handle_credits_click(mx, my)

    def _is_button_pressed(self, rect: pygame.Rect) -> bool:
        if not self.left_mouse_down or self.pressed_button_rect is None:
            return False
        mx, my = pygame.mouse.get_pos()
        return self.pressed_button_rect == rect and rect.collidepoint(mx, my)

    # ---------- UI 初始化 ----------
    def _init_ui(self):
        u = lambda v: int(round(v * self.ui_scale))

        self.btn_q = pygame.Rect(WINDOW_WIDTH - u(172), u(16), u(30), u(30))

        self.btn_home_start = pygame.Rect(self.panel_x + u(20), u(266), u(380), u(44))
        self.btn_home_mode = pygame.Rect(self.panel_x + u(20), u(320), u(380), u(44))
        self.btn_home_option = pygame.Rect(self.panel_x + u(20), u(374), u(380), u(44))
        self.btn_home_english = pygame.Rect(self.panel_x + u(20), u(428), u(380), u(44))
        self.btn_home_credits = pygame.Rect(WINDOW_WIDTH - u(132), u(14), u(110), u(34))

        self.mode_btns = [
            (pygame.Rect(self.panel_x + u(20), u(156), u(380), u(38)), MODE_NORMAL, "普通"),
            (pygame.Rect(self.panel_x + u(20), u(200), u(380), u(38)), MODE_ADV1, "进阶 1 - 单飞禁止"),
            (pygame.Rect(self.panel_x + u(20), u(244), u(380), u(38)), MODE_ADV2, "进阶 2 - 两步验证"),
            (pygame.Rect(self.panel_x + u(20), u(288), u(380), u(38)), MODE_ADV3, "进阶 3 - 暗黑心理学"),
            (pygame.Rect(self.panel_x + u(20), u(332), u(380), u(38)), MODE_ADV4, "进阶 4 - 牛顿摆"),
        ]
        self.btn_mode_back = pygame.Rect(self.panel_x + u(20), WINDOW_HEIGHT - u(54), u(180), u(34))

        self.chk_opt1 = pygame.Rect(self.panel_x + u(20), u(162), u(18), u(18))
        self.chk_opt2 = pygame.Rect(self.panel_x + u(20), u(190), u(18), u(18))
        self.chk_opt3 = pygame.Rect(self.panel_x + u(20), u(218), u(18), u(18))
        self.chk_opt4 = pygame.Rect(self.panel_x + u(20), u(246), u(18), u(18))
        self.chk_opt5 = pygame.Rect(self.panel_x + u(20), u(274), u(18), u(18))
        self.slider_rect = pygame.Rect(self.panel_x + u(44), u(342), u(250), u(10))
        self.slider_drag = False
        self.btn_opt_back = pygame.Rect(self.panel_x + u(20), WINDOW_HEIGHT - u(54), u(180), u(34))

        self.btn_reveal_p1 = pygame.Rect(self.panel_x + u(20), u(150), u(185), u(66))
        self.btn_reveal_p2 = pygame.Rect(self.panel_x + u(220), u(150), u(185), u(66))
        self.btn_reveal_p3 = pygame.Rect(self.panel_x + u(20), u(228), u(185), u(66))
        self.btn_reveal_p4 = pygame.Rect(self.panel_x + u(220), u(228), u(185), u(66))
        self.btn_reveal_start = pygame.Rect(self.panel_x + u(20), u(306), u(385), u(44))
        self.btn_reveal_home = pygame.Rect(self.panel_x + u(220), WINDOW_HEIGHT - u(52), u(180), u(34))

        self.btn_symbol_o = pygame.Rect(self.panel_x + u(20), u(210), u(184), u(50))
        self.btn_symbol_x = pygame.Rect(self.panel_x + u(216), u(210), u(184), u(50))
        self.btn_restart = pygame.Rect(self.panel_x + u(20), WINDOW_HEIGHT - u(52), u(186), u(34))
        self.btn_exit_home = pygame.Rect(self.panel_x + u(214), WINDOW_HEIGHT - u(52), u(186), u(34))

        self.action_area_x = self.panel_x + u(20)
        self.action_area_y = u(270)
        self.action_area_w = u(380)
        self.action_h = u(36)

        self.feedback_rect = pygame.Rect(self.panel_x + u(16), u(344), u(390), u(250))

        self.btn_rule_close = pygame.Rect(0, 0, 0, 0)
        self.btn_rule_prev = pygame.Rect(0, 0, 0, 0)
        self.btn_rule_next = pygame.Rect(0, 0, 0, 0)

        self.btn_credits_back = pygame.Rect(self.panel_x + u(286), WINDOW_HEIGHT - u(52), u(114), u(34))

    # ---------- 日志 ----------
    def _add_feedback(
        self,
        msg: str,
        color: Tuple[int, int, int] = SUB_TEXT,
        bold: bool = False,
        player_pid: Optional[int] = None,
        separator: bool = False,
    ):
        self.feedback.append(FeedbackEntry(msg, color, bold, separator, player_pid))
        if len(self.feedback) > 320:
            self.feedback = self.feedback[-320:]
        self.feedback_scroll_target = 10**9

    def _add_separator(self):
        self._add_feedback("", separator=True)

    # ---------- 对局数据 ----------
    def _new_players(self):
        camps = ["O", "O", "X", "X"]
        random.shuffle(camps)
        colors = PLAYER_COLORS.copy()
        random.shuffle(colors)
        self.players = [Player(i + 1, colors[i], camps[i]) for i in range(4)]
        self.turn_order = sorted(self.players, key=lambda p: p.pid)

    def _prepare_game_from_reveal(self):
        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.pending_piece = None
        self.pending_lines.clear()
        self.last_confirmed_cell = None
        self.opened_line_cells = None
        self.waiting_line_cells = None
        self.rejected_line_cells = None
        self.rejected_line_alpha = 0.0
        self.consent_status_text = ""
        self.selected_symbol = "O"

        self.turn_index = 0
        self.turn_dir = 1
        self.turn_step = 0
        self.turn_time_left = float(self.turn_time_limit)
        self.player_last_symbol = {p.pid: None for p in self.players}
        self.touched_this_turn = False
        self.open_waiting_consent = False
        self.consent_player_pid = None
        self.chosen_line = None

        self.game_over = False
        self.winner_text = ""

        self.feedback.clear()
        self.feedback_scroll_target = 0.0
        self.feedback_scroll_display = 0.0
        mode_name = MODE_NAMES_EN[self.mode] if self.english_mode else MODE_NAMES[self.mode]
        self._add_feedback(self._t(f"对局开始。模式：{mode_name}", f"Game started. Mode: {mode_name}"), HIGHLIGHT, bold=True)
        self._start_turn()

    def _restart_with_new_assignment(self):
        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.pending_piece = None
        self.pending_lines.clear()
        self.last_confirmed_cell = None
        self.opened_line_cells = None
        self.waiting_line_cells = None
        self.rejected_line_cells = None
        self.rejected_line_alpha = 0.0
        self.consent_status_text = ""
        self._new_players()
        self.reveal_hold_pid = None
        self.reveal_viewed.clear()
        self.app_state = AppState.REVEAL

    def current_player(self) -> Player:
        return self.turn_order[self.turn_index]

    def _round_index(self) -> int:
        return self.turn_step // 4 + 1

    def _mode_at_least(self, m: int) -> bool:
        return self.mode >= m

    def _available_symbols(self, player: Player) -> List[str]:
        if self._mode_at_least(MODE_ADV3) and self._round_index() == 1:
            return [self.first_round_symbol_choice]

        if self.option_symbol_alternate and self._round_index() >= 2:
            last = self.player_last_symbol.get(player.pid)
            if last == "O":
                return ["X"]
            if last == "X":
                return ["O"]

        return ["O", "X"]

    def _ensure_symbol_valid(self):
        if not self.turn_order:
            return
        avail = self._available_symbols(self.current_player())
        if self.selected_symbol not in avail:
            self.selected_symbol = avail[0]

    def _start_turn(self):
        if self.game_over:
            return

        self.turn_time_left = float(self.turn_time_limit)
        self.pending_piece = None
        self.pending_lines.clear()
        self.open_waiting_consent = False
        self.consent_player_pid = None
        self.chosen_line = None
        self.hover_open_line_idx = None
        self.hover_open_line_draw_idx = None
        self.hover_open_line_alpha = 0.0
        self.waiting_line_cells = None
        self.consent_status_text = ""
        self.touched_this_turn = False
        self._ensure_symbol_valid()

        if self.option_center_first and self._confirmed_count() == 0:
            center = BOARD_SIZE // 2
            p = self.current_player()
            self.pending_piece = PendingPiece(center, center, self.selected_symbol, p.pid)
            self.pending_lines = self._detect_new_lines_for_pending(self.pending_piece)

    def _advance_turn(self):
        self.turn_step += 1

        if self._mode_at_least(MODE_ADV4):
            if self.turn_step <= 3:
                self.turn_index = (self.turn_index + 1) % 4
            elif self.turn_step == 4:
                self.turn_index = 3
                self.turn_dir = -1
            else:
                if self.turn_dir == 1:
                    if self.turn_index == 3:
                        self.turn_dir = -1
                    else:
                        self.turn_index += 1
                else:
                    if self.turn_index == 0:
                        self.turn_dir = 1
                    else:
                        self.turn_index -= 1
        else:
            self.turn_index = (self.turn_index + 1) % 4

        self._start_turn()

    # ---------- 四连检测 ----------
    def _inside(self, r: int, c: int) -> bool:
        return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE

    def _cell_from_mouse(self, mx: int, my: int) -> Optional[Tuple[int, int]]:
        if not (self.board_x <= mx < self.board_x + BOARD_SIZE * CELL_SIZE):
            return None
        if not (self.board_y <= my < self.board_y + BOARD_SIZE * CELL_SIZE):
            return None
        c = (mx - self.board_x) // CELL_SIZE
        r = (my - self.board_y) // CELL_SIZE
        return int(r), int(c)

    def _confirmed_count(self) -> int:
        return sum(1 for r in range(BOARD_SIZE) for c in range(BOARD_SIZE) if self.board[r][c] is not None)

    def _snapshot_symbols(self) -> List[List[Optional[str]]]:
        s = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                p = self.board[r][c]
                s[r][c] = p.symbol if p else None
        return s

    def _lines_including(self, sym_board: List[List[Optional[str]]], row: int, col: int) -> Dict[Tuple[str, Tuple[Tuple[int, int], ...]], str]:
        result: Dict[Tuple[str, Tuple[Tuple[int, int], ...]], str] = {}
        dirs = [(1, 0, "V"), (0, 1, "H"), (1, 1, "D1"), (1, -1, "D2")]
        n = 4
        for dr, dc, dname in dirs:
            for off in range(-(n - 1), 1):
                cells = []
                for k in range(n):
                    rr = row + (off + k) * dr
                    cc = col + (off + k) * dc
                    if not self._inside(rr, cc):
                        cells = []
                        break
                    cells.append((rr, cc))
                if len(cells) != n:
                    continue

                s0 = sym_board[cells[0][0]][cells[0][1]]
                if s0 is None:
                    continue
                if all(sym_board[r][c] == s0 for r, c in cells):
                    result[(s0, tuple(sorted(cells)))] = dname
        return result

    def _owner_with_pending(self, r: int, c: int, pending: PendingPiece) -> int:
        if r == pending.row and c == pending.col:
            return pending.owner_pid
        p = self.board[r][c]
        return p.owner_pid if p else -1

    def _detect_new_lines_for_pending(self, pending: PendingPiece) -> List[LineCandidate]:
        before = self._snapshot_symbols()
        after = [row[:] for row in before]
        after[pending.row][pending.col] = pending.symbol

        old_lines = self._lines_including(before, pending.row, pending.col)
        new_lines = self._lines_including(after, pending.row, pending.col)

        out: List[LineCandidate] = []
        for key, d in new_lines.items():
            if key in old_lines:
                continue
            sym, cells = key
            out.append(LineCandidate(sym, list(cells), d))
        return out

    def _can_open_line(self, line: LineCandidate, opener_pid: int) -> bool:
        if self.pending_piece is None:
            return False

        owners = {self._owner_with_pending(r, c, self.pending_piece) for r, c in line.cells}
        owners.discard(-1)

        if len(owners) > 2:
            return False
        if self._mode_at_least(MODE_ADV1) and len(owners) == 1:
            return False
        if self._mode_at_least(MODE_ADV2):
            others = [x for x in owners if x != opener_pid]
            if not others:
                return False
        return True

    def _open_line_choices(self) -> List[Tuple[int, str]]:
        if self.pending_piece is None:
            return []

        opener = self.current_player().pid
        valid_indices = [i for i, ln in enumerate(self.pending_lines) if self._can_open_line(ln, opener)]
        if not valid_indices:
            return []

        dirs = {
            "H": "横向",
            "V": "纵向",
            "D1": "斜向（左上 - 右下）",
            "D2": "斜向（右上 - 左下）",
        }
        grouped: Dict[str, List[int]] = {"H": [], "V": [], "D1": [], "D2": []}
        for i in valid_indices:
            d = self.pending_lines[i].direction
            if d in grouped:
                grouped[d].append(i)

        active_dirs = [d for d in ("H", "V", "D1", "D2") if grouped[d]]
        single_dir_only = len(active_dirs) == 1
        use_diag_detail = bool(grouped["D1"] and grouped["D2"]) and not single_dir_only

        result: List[Tuple[int, str]] = []
        for d in ("H", "V", "D1", "D2"):
            arr = grouped[d]
            if not arr:
                continue
            base_label = ""
            if not single_dir_only:
                base_label = dirs[d]
                if d in ("D1", "D2") and not use_diag_detail:
                    base_label = "斜向"
            arr.sort(key=lambda idx: tuple(sorted(self.pending_lines[idx].cells)))
            if len(arr) == 1:
                result.append((arr[0], base_label if base_label else "开盒"))
            else:
                for k, idx in enumerate(arr, start=1):
                    result.append((idx, f"{base_label} #{k}" if base_label else f"开盒 #{k}"))

        return result

    def _board_full(self) -> bool:
        return all(self.board[r][c] is not None for r in range(BOARD_SIZE) for c in range(BOARD_SIZE))

    # ---------- 结算 ----------
    def _finalize_game(self, text: str):
        self.game_over = True
        self.winner_text = text

        self._add_separator()
        self._add_feedback(self._t("身份揭示：", "Team Reveal:"), TEXT_COLOR, bold=True)
        for pl in self.players:
            camp = self._t("圈 (O)", "Circle (O)") if pl.camp == "O" else self._t("叉 (X)", "Cross (X)")
            self._add_feedback(f"{self._pn(pl.pid)} → {camp}", SUB_TEXT, player_pid=pl.pid)

        self._add_separator()
        self._add_feedback(text, TEXT_COLOR, bold=True)

    def _commit_pending_without_open(self, reason: str):
        if self.pending_piece is None:
            return

        self.opened_line_cells = None
        self.waiting_line_cells = None
        self.consent_status_text = ""

        p = self.pending_piece
        self.board[p.row][p.col] = Piece(p.symbol, p.owner_pid)
        self._play_sfx("confirm")
        self.player_last_symbol[p.owner_pid] = p.symbol
        self.last_confirmed_cell = (p.row, p.col)
        self._add_feedback(reason, SUB_TEXT, player_pid=p.owner_pid)

        self.pending_piece = None
        self.pending_lines.clear()
        self.open_waiting_consent = False
        self.consent_player_pid = None
        self.chosen_line = None

        if self._board_full():
            self._finalize_game(self._t("棋盘已满，和棋并揭示阵营。", "Board is full. Draw, then reveal teams."))
        else:
            self._advance_turn()

    def _evaluate_open_line(self, line: LineCandidate):
        if self.pending_piece is None:
            return

        opener = self.current_player()
        opener_camp = opener.camp

        owners = [self._owner_with_pending(r, c, self.pending_piece) for r, c in line.cells]
        owner_camps = [self.players[pid - 1].camp for pid in owners]
        success = all(c == opener_camp for c in owner_camps) and (line.symbol == opener_camp)

        p = self.pending_piece
        self.board[p.row][p.col] = Piece(p.symbol, p.owner_pid)
        self._play_sfx("confirm")
        self.player_last_symbol[p.owner_pid] = p.symbol
        self.last_confirmed_cell = (p.row, p.col)
        self.pending_piece = None
        self.pending_lines.clear()

        owner_set = set(owners)
        all_throwing_by_symbol = all(self.players[pid - 1].camp != line.symbol for pid in owner_set)
        self.opened_line_cells = list(line.cells)
        if self._mode_at_least(MODE_ADV2) and self.consent_player_pid is not None:
            consent_camp = self.players[self.consent_player_pid - 1].camp
            if consent_camp != opener_camp and line.symbol != opener_camp:
                camp_name = self._t("圈 (O)", "Circle (O)") if opener_camp == "O" else self._t("叉 (X)", "Cross (X)")
                self._finalize_game(self._t(f"得吃了！{camp_name} 阵营获胜。", f"Gotcha ! {camp_name} team wins."))
                return
        if success:
            camp_name = self._t("圈 (O)", "Circle (O)") if opener_camp == "O" else self._t("叉 (X)", "Cross (X)")
            self._finalize_game(self._t(f"就是你！{camp_name} 阵营获胜。", f"I knew it ! {camp_name} team wins."))
        else:
            opp = "X" if opener_camp == "O" else "O"
            camp_name = self._t("圈 (O)", "Circle (O)") if opp == "O" else self._t("叉 (X)", "Cross (X)")
            if self.mode == MODE_NORMAL and len(owner_set) == 1 and all_throwing_by_symbol:
                self._finalize_game(self._t(f"你干嘛哈哈哎哟~{camp_name} 阵营获胜。", f"Quoi t'fais ? {camp_name} team wins."))
            elif len(owner_set) == 2 and all_throwing_by_symbol:
                self._finalize_game(self._t(f"你俩干嘛哈哈哎哟~{camp_name} 阵营获胜。", f"Quoi vous faites ? {camp_name} team wins."))
            else:
                self._finalize_game(self._t(f"你居然！{camp_name} 阵营获胜。", f"Liar ! {camp_name} team wins."))

    # ---------- 动作按钮 ----------
    def _action_buttons(self) -> List[Tuple[pygame.Rect, str, Optional[int]]]:
        buttons: List[Tuple[pygame.Rect, str, Optional[int]]] = []
        u = self._u
        if self.game_over:
            return buttons

        if self.open_waiting_consent:
            buttons.append((pygame.Rect(self.action_area_x, self.action_area_y, u(184), self.action_h), "agree", 1))
            buttons.append((pygame.Rect(self.action_area_x + u(196), self.action_area_y, u(184), self.action_h), "reject", 0))
            return buttons

        if self.pending_piece is None:
            buttons.append((pygame.Rect(self.action_area_x, self.action_area_y, self.action_area_w, self.action_h), "confirm_disabled", None))
            return buttons

        if not self.pending_lines:
            buttons.append((pygame.Rect(self.action_area_x, self.action_area_y, self.action_area_w, self.action_h), "confirm", None))
            return buttons

        choices = self._open_line_choices()
        if len(choices) == 0:
            buttons.append((pygame.Rect(self.action_area_x, self.action_area_y, self.action_area_w, self.action_h), "no_open", None))
            return buttons

        if len(choices) == 1 and len(self.pending_lines) == 1:
            y = self.action_area_y
            buttons.append((pygame.Rect(self.action_area_x, y, self.action_area_w, self.action_h), "open_line", choices[0][0]))
            y += self.action_h + u(6)
            buttons.append((pygame.Rect(self.action_area_x, y, self.action_area_w, self.action_h), "no_open", None))
            return buttons

        y = self.action_area_y
        for idx, _ in choices:
            buttons.append((pygame.Rect(self.action_area_x, y, self.action_area_w, self.action_h), "open_line", idx))
            y += self.action_h + u(6)
        buttons.append((pygame.Rect(self.action_area_x, y, self.action_area_w, self.action_h), "no_open", None))
        return buttons

    def _action_viewport_rect(self) -> pygame.Rect:
        top = self.action_area_y
        bottom = self.feedback_rect.y - 10
        h = max(self.action_h, bottom - top)
        return pygame.Rect(self.action_area_x, top, self.action_area_w, h)

    def _action_buttons_view(self) -> Tuple[List[Tuple[pygame.Rect, str, Optional[int]]], bool, int]:
        raw = self._action_buttons()
        if not raw:
            self.action_thumb_rect = pygame.Rect(0, 0, 0, 0)
            self.action_scroll_target = 0.0
            self.action_scroll_display = 0.0
            return [], False, 0

        view = self._action_viewport_rect()
        min_y = min(r.y for r, _, _ in raw)
        max_bottom = max(r.bottom for r, _, _ in raw)
        total_h = max_bottom - min_y
        max_scroll = max(0, total_h - view.height)
        content_w = self.action_area_w - 14 if max_scroll > 0 else self.action_area_w

        self.action_scroll_target = max(0.0, min(self.action_scroll_target, float(max_scroll)))
        off = int(round(self.action_scroll_display))

        out: List[Tuple[pygame.Rect, str, Optional[int]]] = []
        for rect, kind, payload in raw:
            rr = rect.move(0, -off)
            if content_w != self.action_area_w:
                rr.width = min(rr.width, content_w)
            if rr.bottom < view.top or rr.top > view.bottom:
                continue
            out.append((rr, kind, payload))
        return out, max_scroll > 0, max_scroll

    def _update_hover_open_line(self):
        self.hover_open_line_idx = None
        if self.app_state != AppState.GAME or self.game_over:
            return
        if self.pending_piece is None or self.open_waiting_consent:
            return
        self._layout_game_panel_controls()
        mx, my = pygame.mouse.get_pos()
        items, _, _ = self._action_buttons_view()
        for rect, kind, payload in items:
            if kind == "open_line" and payload is not None and rect.collidepoint(mx, my):
                self.hover_open_line_idx = payload
                return

    def _action_button_text(self, kind: str, payload: Optional[int]) -> str:
        if kind == "confirm":
            return self._t("确定", "Confirm")
        if kind == "confirm_disabled":
            return self._t("确定", "Confirm")
        if kind == "no_open":
            return self._t("确定但不开盒", "Confirm (No Open)")
        if kind == "agree":
            return self._t("同意开盒", "Agree to Open")
        if kind == "reject":
            return self._t("不同意开盒", "Reject Open")

        if kind == "open_line" and payload is not None:
            choices = self._open_line_choices()
            label_map = {idx: label for idx, label in choices}
            label = label_map.get(payload, "斜向")

            if label == "开盒":
                return self._t("确定并开盒", "Confirm + Open")
            if label.startswith("开盒 #"):
                tail = label[len("开盒"):]
                return self._t(f"确定并开盒{tail}", f"Confirm + Open{tail}")

            if self.english_mode:
                lmap = {
                    "横向": "Confirm + Open Horiz",
                    "纵向": "Confirm + Open Vert",
                    "斜向": "Confirm + Open Diag",
                    "斜向（左上 - 右下）": "Confirm + Open Diag ( topL to btmR )",
                    "斜向（右上 - 左下）": "Confirm + Open Diag ( topR to btmL )",
                }
                base = label.split(" #", 1)[0]
                tail = ""
                if " #" in label:
                    tail = " #" + label.split(" #", 1)[1]
                return lmap.get(base, "Confirm + Open Diag") + tail
            return f"确定并{label}开盒"

        return self._t("确定", "Confirm")

    # ---------- 超时 ----------
    def _on_timeout(self):
        if self.game_over:
            return

        if self.pending_piece is not None:
            p = self.pending_piece
            self._commit_pending_without_open(
                self._t(
                    f"{self._pn(p.owner_pid)} 超时：已自动确认 {p.symbol} 于 {self._coord(p.row, p.col)}，不开盒。",
                    f"{self._pn(p.owner_pid)} timed out: auto-confirmed {p.symbol} at {self._coord(p.row, p.col)} without box-opening.",
                )
            )
            return

        if not self.touched_this_turn:
            pid = self.current_player().pid
            self._add_feedback(self._t(f"{self._pn(pid)} 超时，自动跳过。", f"{self._pn(pid)} timed out, auto-skipped."), SUB_TEXT, player_pid=pid)
            if self._board_full():
                self._finalize_game(self._t("棋盘已满，和棋并揭示阵营。", "Board is full. Draw, then reveal teams."))
            else:
                self._advance_turn()

    # ---------- 绘制工具 ----------
    def _button_text_scale(self, key: str, hovered: bool) -> float:
        cur = self.button_hover_scale.get(key, 1.0)
        target = 1.08 if hovered else 1.0
        cur += (target - cur) * 0.28
        self.button_hover_scale[key] = cur
        return cur

    def _pulse_linear01(self, cycle_sec: float = 1.083) -> float:
        t = pygame.time.get_ticks() / 1000.0
        p = (t / max(0.001, cycle_sec)) % 1.0
        return 1.0 - abs(2.0 * p - 1.0)

    def _blit_scaled_center(self, src: pygame.Surface, center: Tuple[int, int], scale: float):
        if abs(scale - 1.0) < 0.01:
            self.screen.blit(src, (center[0] - src.get_width() // 2, center[1] - src.get_height() // 2))
            return
        nw = max(1, int(round(src.get_width() * scale)))
        nh = max(1, int(round(src.get_height() * scale)))
        scaled = pygame.transform.scale(src, (nw, nh))
        self.screen.blit(scaled, (center[0] - nw // 2, center[1] - nh // 2))

    def _fit_button_text(self, font: pygame.font.Font, text: str, color: Tuple[int, int, int], max_w: int, base_scale: float) -> Tuple[pygame.Surface, float]:
        scaled_limit = max_w
        if base_scale > 1.0:
            scaled_limit = max(10, int(max_w / base_scale))
        img = font.render(text, True, color)
        if img.get_width() <= scaled_limit:
            return img, base_scale
        short = text
        while len(short) > 3:
            short = short[:-1]
            candidate = short + "..."
            test = font.render(candidate, True, color)
            if test.get_width() <= scaled_limit:
                return test, base_scale
        return img, base_scale

    def _draw_status_option(self, x: int, y: int, checked: bool, text: str, color: Tuple[int, int, int] = SUB_TEXT, readonly: bool = False):
        u = self._u
        box = pygame.Rect(x, y + u(1), u(16), u(16))
        if readonly:
            fill = (46, 56, 82)
            border = (90, 108, 150)
            tick = (209, 177, 102)
            text_color = (146, 156, 180)
        else:
            fill = (62, 78, 115)
            border = (132, 158, 213)
            tick = HIGHLIGHT
            text_color = color

        pygame.draw.rect(self.screen, fill, box, border_radius=3)
        pygame.draw.rect(self.screen, border, box, 2, border_radius=3)
        if checked:
            pygame.draw.line(self.screen, tick, (box.x + u(3), box.y + u(8)), (box.x + u(7), box.y + u(13)), max(1, u(2)))
            pygame.draw.line(self.screen, tick, (box.x + u(7), box.y + u(13)), (box.x + u(13), box.y + u(3)), max(1, u(2)))
        self.screen.blit(self.font_rule.render(text, True, text_color), (x + u(22), y - u(1)))

    def _draw_text_button(self, rect: pygame.Rect, text: str, active: bool = False, disabled: bool = False):
        pressed = self._is_button_pressed(rect)
        mx, my = pygame.mouse.get_pos()
        hovered = rect.collidepoint(mx, my)
        sx = self._disabled_button_shake_offset(rect) if disabled else 0
        draw_rect = rect.move(sx, 0)
        if disabled:
            fill, border, color = (56, 62, 78), (76, 86, 110), DISABLED_TEXT
        else:
            fill, border, color = (76, 104, 166), (126, 156, 218), TEXT_COLOR
            if active:
                fill, border = (111, 152, 244), HIGHLIGHT
            if pressed:
                fill, border = (58, 80, 128), (104, 132, 186)
        pygame.draw.rect(self.screen, fill, draw_rect, border_radius=8)
        pygame.draw.rect(self.screen, border, draw_rect, 2, border_radius=8)
        img = self.font_small.render(text, True, color)
        dx = 1 if pressed and not disabled else 0
        dy = 1 if pressed and not disabled else 0
        key = f"{draw_rect.x},{draw_rect.y},{draw_rect.width},{draw_rect.height}:{text}"
        scale = self._button_text_scale(key, hovered)
        img, scale = self._fit_button_text(self.font_small, text, color, max(10, draw_rect.width - 18), scale)
        center = (draw_rect.centerx + dx, draw_rect.centery + dy)
        self._blit_scaled_center(img, center, scale)

    def _draw_q_button(self):
        pressed = self._is_button_pressed(self.btn_q)
        mx, my = pygame.mouse.get_pos()
        hovered = self.btn_q.collidepoint(mx, my)
        fill = (58, 82, 130) if pressed else (74, 102, 162)
        border = (122, 148, 208) if pressed else (150, 180, 238)
        pygame.draw.circle(self.screen, fill, self.btn_q.center, 15)
        pygame.draw.circle(self.screen, border, self.btn_q.center, 15, 2)
        q = self.font_small.render("?", True, TEXT_COLOR)
        dx = 1 if pressed else 0
        dy = 1 if pressed else 0
        scale = self._button_text_scale("btn_q:?", hovered)
        center = (self.btn_q.centerx + dx, self.btn_q.centery - 1 + dy)
        self._blit_scaled_center(q, center, scale)

    def _draw_symbol(self, surf: pygame.Surface, symbol: str, center: Tuple[int, int], color: Tuple[int, ...], radius: int, width: int):
        x, y = center
        w = max(width + 1, int(round(width * self.ui_scale)))
        if symbol == "O":
            pygame.draw.circle(surf, color, center, radius, w)
        else:
            rr = int(radius * 0.82)
            xw = max(w + 1, int(round(w * 1.2)))
            pygame.draw.line(surf, color, (x - rr, y - rr), (x + rr, y + rr), xw)
            pygame.draw.line(surf, color, (x - rr, y + rr), (x + rr, y - rr), xw)

    def _wrap_text(self, text: str, font: pygame.font.Font, width: int) -> List[str]:
        lines: List[str] = []
        cur = ""
        for ch in text:
            t = cur + ch
            if font.size(t)[0] <= width or cur == "":
                cur = t
            else:
                lines.append(cur)
                cur = ch
        if cur:
            lines.append(cur)

        if lines:
            leading_punct = set("，。！？；：、）】》〉」』,.!?;:)]}")
            i = 1
            while i < len(lines):
                if lines[i] and lines[i - 1]:
                    moved = False
                    while lines[i] and lines[i][0] in leading_punct:
                        ch = lines[i][0]
                        allow_w = width + font.size(ch)[0]
                        if font.size(lines[i - 1] + ch)[0] <= allow_w:
                            lines[i - 1] += ch
                            lines[i] = lines[i][1:]
                            moved = True
                        else:
                            break
                    if moved and lines[i] == "":
                        lines.pop(i)
                        continue
                i += 1
        return lines

    def _wrap_text_smart(self, text: str, font: pygame.font.Font, width: int) -> List[str]:
        if not self.english_mode or " " not in text:
            return self._wrap_text(text, font, width)

        words = text.split(" ")
        lines: List[str] = []
        cur = ""
        for w in words:
            t = w if cur == "" else f"{cur} {w}"
            if font.size(t)[0] <= width:
                cur = t
                continue

            if cur:
                lines.append(cur)
                cur = ""

            if font.size(w)[0] <= width:
                cur = w
            else:
                parts = self._wrap_text(w, font, width)
                if parts:
                    lines.extend(parts[:-1])
                    cur = parts[-1]

        if cur:
            lines.append(cur)
        return lines

    # ---------- 绘制主面板 ----------
    def _draw_hover_hint_panel(self, text: str, height: int = 110):
        u = self._u
        panel = pygame.Rect(self.panel_x + u(20), u(438), u(380), u(height))
        pygame.draw.rect(self.screen, (27, 35, 52), panel, border_radius=10)
        pygame.draw.rect(self.screen, (96, 122, 176), panel, 1, border_radius=10)

        lines = self._wrap_text(text, self.font_rule, panel.width - 20)
        y = panel.y + u(10)
        for line in lines:
            self.screen.blit(self.font_rule.render(line, True, SUB_TEXT), (panel.x + u(10), y))
            y += u(20)
            if y > panel.bottom - u(18):
                break

    def _draw_hover_hint_panel_fade(self, text: str, height: int = 110):
        u = self._u
        target = 1.0 if text else 0.0
        self.hover_hint_alpha += (target - self.hover_hint_alpha) * 0.22
        if text:
            self.hover_hint_text = text
        if self.hover_hint_alpha <= 0.01:
            return

        panel = pygame.Rect(self.panel_x + u(20), u(438), u(380), u(height))
        surf = pygame.Surface((panel.width, panel.height), pygame.SRCALPHA)
        pygame.draw.rect(surf, (27, 35, 52, 255), (0, 0, panel.width, panel.height), border_radius=10)
        pygame.draw.rect(surf, (96, 122, 176, 255), (0, 0, panel.width, panel.height), 1, border_radius=10)

        lines = self._wrap_text(self.hover_hint_text, self.font_rule, panel.width - u(20))
        y = u(10)
        for line in lines:
            surf.blit(self.font_rule.render(line, True, SUB_TEXT), (u(10), y))
            y += u(20)
            if y > panel.height - u(18):
                break

        surf.set_alpha(int(255 * self.hover_hint_alpha))
        self.screen.blit(surf, panel.topleft)

    def _wrap_text_preserve_player_names(self, text: str, font: pygame.font.Font, width: int) -> List[str]:
        if not text:
            return [""]
        names = [self._pn(p.pid) for p in self.players]
        names.sort(key=len, reverse=True)

        tokens: List[str] = []
        i = 0
        n = len(text)
        while i < n:
            hit = None
            for name in names:
                if text.startswith(name, i):
                    hit = name
                    break
            if hit is not None:
                tokens.append(hit)
                i += len(hit)
            else:
                if self.english_mode:
                    if text[i].isspace():
                        tokens.append(text[i])
                        i += 1
                    else:
                        j = i + 1
                        while j < n:
                            if text[j].isspace():
                                break
                            if any(text.startswith(name, j) for name in names):
                                break
                            j += 1
                        tokens.append(text[i:j])
                        i = j
                else:
                    tokens.append(text[i])
                    i += 1

        lines: List[str] = []
        cur = ""
        for tk in tokens:
            if self.english_mode and tk.isspace() and cur == "":
                continue
            t = cur + tk
            if font.size(t)[0] <= width or cur == "":
                cur = t
            else:
                lines.append(cur.rstrip() if self.english_mode else cur)
                if font.size(tk)[0] <= width:
                    cur = tk.lstrip() if self.english_mode else tk
                else:
                    parts = self._wrap_text(tk, font, width)
                    lines.extend(parts[:-1])
                    cur = parts[-1] if parts else ""

        if cur:
            lines.append(cur)
        return lines

    def _feedback_rows(self, max_sep_w: int) -> List[dict]:
        rows: List[dict] = []
        for entry in self.feedback:
            if entry.separator:
                rows.append({"kind": "sep"})
                continue

            font = self.font_rule_bold if entry.bold else self.font_rule
            if entry.player_pid is not None:
                prefix = self._pn(entry.player_pid)
                if entry.text.startswith(prefix):
                    pc = self.players[entry.player_pid - 1].color
                    tail = entry.text[len(prefix):]
                    if self.english_mode:
                        tail = tail.lstrip()
                        indent = max(0, font.size(prefix + " ")[0])
                    else:
                        indent = max(0, font.size(prefix)[0])
                    wrap_w = max(10, max_sep_w - indent)
                    parts = self._wrap_text_preserve_player_names(tail if tail else " ", font, wrap_w)
                    rows.append({
                        "kind": "player_first",
                        "font": font,
                        "prefix": prefix,
                        "prefix_color": pc,
                        "text": parts[0],
                        "color": entry.color,
                        "indent": indent,
                    })
                    for p in parts[1:]:
                        rows.append({
                            "kind": "player_cont",
                            "font": font,
                            "text": p,
                            "color": entry.color,
                            "indent": indent,
                        })
                    continue

            for part in self._wrap_text_preserve_player_names(entry.text if entry.text else " ", font, max_sep_w):
                rows.append({"kind": "text", "font": font, "text": part, "color": entry.color})
        return rows

    def _blit_feedback_text_with_player_colors(self, font: pygame.font.Font, text: str, base_color: Tuple[int, int, int], x: int, y: int):
        if not text:
            return
        names = [(self._pn(p.pid), p.color) for p in self.players]
        names.sort(key=lambda t: len(t[0]), reverse=True)

        cx = x
        i = 0
        n = len(text)
        while i < n:
            hit_name = None
            hit_color = None
            for name, pc in names:
                if text.startswith(name, i):
                    hit_name = name
                    hit_color = pc
                    break

            if hit_name is None:
                j = i + 1
                while j < n:
                    if any(text.startswith(name, j) for name, _ in names):
                        break
                    j += 1
                seg = text[i:j]
                img = font.render(seg, True, base_color)
                self.screen.blit(img, (cx, y))
                cx += img.get_width()
                i = j
            else:
                img = font.render(hit_name, True, hit_color if hit_color is not None else base_color)
                self.screen.blit(img, (cx, y))
                cx += img.get_width()
                i += len(hit_name)

    def _render_player_colored_line(self, font: pygame.font.Font, text: str, base_color: Tuple[int, int, int]) -> pygame.Surface:
        w = max(1, font.size(text)[0])
        h = max(1, font.get_height())
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        names = [(self._pn(p.pid), p.color) for p in self.players]
        names.sort(key=lambda t: len(t[0]), reverse=True)

        cx = 0
        i = 0
        n = len(text)
        while i < n:
            hit_name = None
            hit_color = None
            for name, pc in names:
                if text.startswith(name, i):
                    hit_name = name
                    hit_color = pc
                    break

            if hit_name is None:
                j = i + 1
                while j < n:
                    if any(text.startswith(name, j) for name, _ in names):
                        break
                    j += 1
                seg = text[i:j]
                img = font.render(seg, True, base_color)
                surf.blit(img, (cx, 0))
                cx += img.get_width()
                i = j
            else:
                img = font.render(hit_name, True, hit_color if hit_color is not None else base_color)
                surf.blit(img, (cx, 0))
                cx += img.get_width()
                i += len(hit_name)
        return surf

    def _draw_feedback(self):
        u = self._u
        pygame.draw.rect(self.screen, (24, 31, 48), self.feedback_rect, border_radius=10)
        pygame.draw.rect(self.screen, (82, 104, 152), self.feedback_rect, 1, border_radius=10)
        self.screen.blit(self.font_small.render("Breaking News !", True, TEXT_COLOR), (self.feedback_rect.x + u(10), self.feedback_rect.y + u(8)))

        header_sep = "-" * 120
        max_header_w = self.feedback_rect.width - 30
        while self.font_rule.size(header_sep)[0] > max_header_w and len(header_sep) > 1:
            header_sep = header_sep[:-1]
        self.screen.blit(self.font_rule.render(header_sep, True, (110, 124, 156)), (self.feedback_rect.x + u(10), self.feedback_rect.y + u(24)))

        content_x = self.feedback_rect.x + u(10)
        content_y = self.feedback_rect.y + u(40)
        content_h = self.feedback_rect.height - u(44)
        scrollbar_w = u(10)
        line_h = max(self.font_rule.get_height() + u(4), u(20))
        visible = max(1, content_h // line_h)

        track_x = self.feedback_rect.right - u(14)
        max_sep_w = track_x - content_x - u(6)
        rows = self._feedback_rows(max_sep_w)

        max_scroll = max(0, len(rows) - visible)
        self.feedback_scroll_target = max(0.0, min(self.feedback_scroll_target, float(max_scroll)))

        start = int(round(self.feedback_scroll_display))
        start = max(0, min(start, max_scroll))
        end = min(len(rows), start + visible)

        y = content_y
        for row in rows[start:end]:
            if row["kind"] == "sep":
                sep = "-" * 200
                while self.font_rule.size(sep)[0] > max_sep_w and len(sep) > 1:
                    sep = sep[:-1]
                self.screen.blit(self.font_rule.render(sep, True, (110, 124, 156)), (content_x, y))
                y += line_h
                continue

            if row["kind"] == "player_first":
                p_img = row["font"].render(row["prefix"], True, row["prefix_color"])
                self.screen.blit(p_img, (content_x, y))
                self._blit_feedback_text_with_player_colors(row["font"], row["text"], row["color"], content_x + row["indent"], y)
            elif row["kind"] == "player_cont":
                self._blit_feedback_text_with_player_colors(row["font"], row["text"], row["color"], content_x + row["indent"], y)
            else:
                self._blit_feedback_text_with_player_colors(row["font"], row["text"], row["color"], content_x, y)
            y += line_h

        track_y = content_y
        track_h = visible * line_h
        pygame.draw.rect(self.screen, (54, 65, 92), (track_x, track_y, scrollbar_w, track_h), border_radius=5)
        u = self._u

        if len(rows) > visible:
            thumb_h = max(u(24), int(track_h * (visible / len(rows))))
            move_range = track_h - thumb_h
            ratio = self.feedback_scroll_display / max_scroll if max_scroll > 0 else 0.0
            thumb_y = track_y + int(move_range * ratio)
            self.feedback_thumb_rect = pygame.Rect(track_x, thumb_y, scrollbar_w, thumb_h)
            pygame.draw.rect(self.screen, (140, 170, 235), self.feedback_thumb_rect, border_radius=5)
        else:
            self.feedback_thumb_rect = pygame.Rect(track_x, track_y, scrollbar_w, track_h)
            pygame.draw.rect(self.screen, (100, 120, 170), self.feedback_thumb_rect, border_radius=5)

    def _draw_board(self):
        piece_w = max(4, self._u(5))
        board_rect = pygame.Rect(self.board_x, self.board_y, BOARD_SIZE * CELL_SIZE, BOARD_SIZE * CELL_SIZE)
        pygame.draw.rect(self.screen, BOARD_BG, board_rect, border_radius=12)
        pygame.draw.rect(self.screen, GRID_COLOR, board_rect, 2, border_radius=12)

        for i in range(BOARD_SIZE):
            tx = self.font_rule.render(f"{i + 1}x", True, SUB_TEXT)
            ty = self.font_rule.render(f"{i + 1}y", True, SUB_TEXT)
            cx = self.board_x + i * CELL_SIZE + CELL_SIZE // 2
            cy = self.board_y + i * CELL_SIZE + CELL_SIZE // 2
            self.screen.blit(tx, (cx - tx.get_width() // 2, self.board_y - tx.get_height() - 2))
            self.screen.blit(ty, (self.board_x - ty.get_width() - 2, cy - ty.get_height() // 2))

        for i in range(1, BOARD_SIZE):
            x = self.board_x + i * CELL_SIZE
            y = self.board_y + i * CELL_SIZE
            pygame.draw.line(self.screen, GRID_COLOR, (x, self.board_y), (x, self.board_y + BOARD_SIZE * CELL_SIZE), 1)
            pygame.draw.line(self.screen, GRID_COLOR, (self.board_x, y), (self.board_x + BOARD_SIZE * CELL_SIZE, y), 1)

        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = self.board[r][c]
                if piece is None:
                    continue
                cx = self.board_x + c * CELL_SIZE + CELL_SIZE // 2
                cy = self.board_y + r * CELL_SIZE + CELL_SIZE // 2
                color = self.players[piece.owner_pid - 1].color if 1 <= piece.owner_pid <= len(self.players) else TEXT_COLOR
                self._draw_symbol(self.screen, piece.symbol, (cx, cy), color, CELL_SIZE // 3, piece_w)

        if self.pending_piece is not None:
            pr, pc = self.pending_piece.row, self.pending_piece.col
            px = self.board_x + pc * CELL_SIZE
            py = self.board_y + pr * CELL_SIZE
            cx = px + CELL_SIZE // 2
            cy = py + CELL_SIZE // 2
            pcolor = self.players[self.pending_piece.owner_pid - 1].color if 1 <= self.pending_piece.owner_pid <= len(self.players) else HIGHLIGHT

            if self.open_waiting_consent:
                alpha = 255
            else:
                alpha_ratio = 0.2 + 0.6 * self._pulse_linear01()
                alpha = max(51, min(204, int(alpha_ratio * 255)))
            layer = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            self._draw_symbol(layer, self.pending_piece.symbol, (CELL_SIZE // 2, CELL_SIZE // 2), (*pcolor[:3], alpha), CELL_SIZE // 3, piece_w)
            self.screen.blit(layer, (px, py))

        if self.hover_open_line_draw_idx is not None and self.hover_open_line_alpha > 0.01 and 0 <= self.hover_open_line_draw_idx < len(self.pending_lines):
            ln = self.pending_lines[self.hover_open_line_draw_idx]
            alpha = int(220 * max(0.0, min(1.0, self.hover_open_line_alpha)))
            glow = (*HIGHLIGHT, alpha)
            layer = pygame.Surface((BOARD_SIZE * CELL_SIZE, BOARD_SIZE * CELL_SIZE), pygame.SRCALPHA)
            bw = max(2, self._u(4))
            inset = max(2, self._u(3))
            for rr, cc in ln.cells:
                x = cc * CELL_SIZE + inset
                y = rr * CELL_SIZE + inset
                pygame.draw.rect(layer, glow, (x, y, CELL_SIZE - inset * 2, CELL_SIZE - inset * 2), bw, border_radius=max(4, self._u(8)))
            self.screen.blit(layer, (self.board_x, self.board_y))

        if self.open_waiting_consent and self.waiting_line_cells and not self.game_over:
            alpha_ratio = 0.2 + 0.6 * self._pulse_linear01()
            alpha = max(64, min(255, int(alpha_ratio * 255)))
            layer = pygame.Surface((BOARD_SIZE * CELL_SIZE, BOARD_SIZE * CELL_SIZE), pygame.SRCALPHA)
            bw = max(2, self._u(4))
            inset = max(2, self._u(3))
            glow = (*HIGHLIGHT, alpha)
            for rr, cc in self.waiting_line_cells:
                x = cc * CELL_SIZE + inset
                y = rr * CELL_SIZE + inset
                pygame.draw.rect(layer, glow, (x, y, CELL_SIZE - inset * 2, CELL_SIZE - inset * 2), bw, border_radius=max(4, self._u(8)))
            self.screen.blit(layer, (self.board_x, self.board_y))

        if self.rejected_line_cells and self.rejected_line_alpha > 0.01:
            alpha = int(220 * max(0.0, min(1.0, self.rejected_line_alpha)))
            layer = pygame.Surface((BOARD_SIZE * CELL_SIZE, BOARD_SIZE * CELL_SIZE), pygame.SRCALPHA)
            bw = max(2, self._u(4))
            inset = max(2, self._u(3))
            glow = (*HIGHLIGHT, alpha)
            for rr, cc in self.rejected_line_cells:
                x = cc * CELL_SIZE + inset
                y = rr * CELL_SIZE + inset
                pygame.draw.rect(layer, glow, (x, y, CELL_SIZE - inset * 2, CELL_SIZE - inset * 2), bw, border_radius=max(4, self._u(8)))
            self.screen.blit(layer, (self.board_x, self.board_y))

        if self.game_over and self.opened_line_cells:
            layer = pygame.Surface((BOARD_SIZE * CELL_SIZE, BOARD_SIZE * CELL_SIZE), pygame.SRCALPHA)
            bw = max(2, self._u(4))
            inset = max(2, self._u(3))
            glow = (*HIGHLIGHT, 230)
            for rr, cc in self.opened_line_cells:
                x = cc * CELL_SIZE + inset
                y = rr * CELL_SIZE + inset
                pygame.draw.rect(layer, glow, (x, y, CELL_SIZE - inset * 2, CELL_SIZE - inset * 2), bw, border_radius=max(4, self._u(8)))
            self.screen.blit(layer, (self.board_x, self.board_y))

        highlight_cell = self.last_confirmed_cell
        if self.open_waiting_consent and self.pending_piece is not None:
            highlight_cell = (self.pending_piece.row, self.pending_piece.col)

        if highlight_cell is not None:
            lr, lc = highlight_cell
            lx = self.board_x + lc * CELL_SIZE
            ly = self.board_y + lr * CELL_SIZE
            pygame.draw.rect(self.screen, (120, 160, 240), (lx + 3, ly + 3, CELL_SIZE - 6, CELL_SIZE - 6), 2, border_radius=8)

    def _draw_game_panel(self):
        u = self._u
        self._layout_game_panel_controls()
        p = self.current_player()
        t1 = self.font_small.render(self._t("当前回合：", "Current Turn: "), True, TEXT_COLOR)
        t2 = self.font_small.render(self._pn(p.pid), True, p.color)
        t3 = self.font_small.render(f"  {max(0, int(self.turn_time_left))} s", True, HIGHLIGHT)
        self.screen.blit(t1, (self.panel_x + u(16), u(24)))
        self.screen.blit(t2, (self.panel_x + u(16) + t1.get_width(), u(24)))
        self.screen.blit(t3, (self.panel_x + u(16) + t1.get_width() + t2.get_width(), u(24)))

        ox = self.panel_x + u(16)
        oy = u(56)
        shake = self._readonly_shake_offset()
        mode_y = oy
        multiline_mode_desc = self.mode == MODE_ADV4 or (self.english_mode and self.mode == MODE_ADV3)
        time_y = oy + (u(44) if multiline_mode_desc else u(22))
        mode_label = self.font_rule_bold.render(self._t("模式：", "Mode: "), True, TEXT_COLOR)
        self.screen.blit(mode_label, (ox, mode_y))
        if self.mode == MODE_ADV4:
            prefix = self._t("进阶 4 - ", "Advanced 4 - ")
            line1 = self._t(
                f"{prefix}牛顿摆、假面舞会 ({self.first_round_symbol_choice})、",
                f"{prefix}Newton's Pendulum, Masquerade ({self.first_round_symbol_choice}),",
            )
            line2 = self._t("两步验证、单飞禁止", "2FA, Solo VFR Banned")
            self.screen.blit(self.font_rule.render(line1, True, SUB_TEXT), (ox + mode_label.get_width(), mode_y))
            indent_x = ox + mode_label.get_width() + self.font_rule.size(prefix)[0]
            self.screen.blit(self.font_rule.render(line2, True, SUB_TEXT), (indent_x, mode_y + u(20)))
        elif self.english_mode and self.mode == MODE_ADV3:
            prefix = "Advanced 3 - "
            line1 = f"{prefix}Masquerade ({self.first_round_symbol_choice}), 2FA,"
            line2 = "Solo VFR Banned"
            self.screen.blit(self.font_rule.render(line1, True, SUB_TEXT), (ox + mode_label.get_width(), mode_y))
            indent_x = ox + mode_label.get_width() + self.font_rule.size(prefix)[0]
            self.screen.blit(self.font_rule.render(line2, True, SUB_TEXT), (indent_x, mode_y + u(20)))
        else:
            mode_value = self.font_rule.render(self._mode_desc(), True, SUB_TEXT)
            self.screen.blit(mode_value, (ox + mode_label.get_width(), mode_y))

        time_label = self.font_rule_bold.render(self._t("时间：", "Time: "), True, TEXT_COLOR)
        time_value = self.font_rule.render(f"{self.turn_time_limit} s", True, SUB_TEXT)
        self.screen.blit(time_label, (ox, time_y))
        self.screen.blit(time_value, (ox + time_label.get_width(), time_y))

        row_base = time_y + u(34)
        self._draw_status_option(ox + shake, row_base, not self.option_disable_chat, self._t("聊天框", "Chat Box"), readonly=True)
        self._draw_status_option(ox + u(168) + shake, row_base, not self.option_disable_mic, self._t("麦克风", "Microphone"), readonly=True)
        self._draw_status_option(ox + shake, row_base + u(22), self.option_center_first, self._t("经典开局", "Classic Start"), readonly=True)
        self._draw_status_option(ox + u(168) + shake, row_base + u(22), self.option_symbol_alternate, self._t("正弦波", "Sine Wave"), readonly=True)

        self._draw_q_button()

        avail = self._available_symbols(p)
        if not self.open_waiting_consent:
            self._draw_text_button(self.btn_symbol_o, "O", self.selected_symbol == "O", "O" not in avail)
            self._draw_text_button(self.btn_symbol_x, "X", self.selected_symbol == "X", "X" not in avail)
        else:
            wait_rect = pygame.Rect(self.btn_symbol_o.x, self.btn_symbol_o.y, self.btn_symbol_x.right - self.btn_symbol_o.x, self.btn_symbol_o.height)
            pygame.draw.rect(self.screen, (56, 66, 92), wait_rect, border_radius=10)
            pygame.draw.rect(self.screen, (90, 114, 170), wait_rect, 2, border_radius=10)

        action_items, scrollable, max_scroll = self._action_buttons_view()
        view = self._action_viewport_rect()
        prev_clip = self.screen.get_clip()
        self.screen.set_clip(view)
        for rect, kind, payload in action_items:
            self._draw_text_button(rect, self._action_button_text(kind, payload), active=(kind != "confirm_disabled"), disabled=(kind == "confirm_disabled"))
        self.screen.set_clip(prev_clip)

        if scrollable:
            track_x = view.right - 10
            track_y = view.y
            track_h = view.height
            scrollbar_w = 8
            pygame.draw.rect(self.screen, (54, 65, 92), (track_x, track_y, scrollbar_w, track_h), border_radius=5)

            thumb_h = max(24, int(track_h * (view.height / (view.height + max_scroll))))
            move_range = track_h - thumb_h
            ratio = self.action_scroll_display / max_scroll if max_scroll > 0 else 0.0
            thumb_y = track_y + int(move_range * ratio)
            self.action_thumb_rect = pygame.Rect(track_x, thumb_y, scrollbar_w, thumb_h)
            pygame.draw.rect(self.screen, (140, 170, 235), self.action_thumb_rect, border_radius=5)
        else:
            self.action_thumb_rect = pygame.Rect(0, 0, 0, 0)

        if self.open_waiting_consent and self.consent_player_pid is not None:
            if self.consent_status_text:
                alpha = 255
                msg = self.consent_status_text
            else:
                alpha_ratio = 0.2 + 0.6 * self._pulse_linear01()
                alpha = max(64, min(255, int(alpha_ratio * 255)))
                msg = self._t(f"等待 {self._pn(self.consent_player_pid)} 二次验证", f"Waiting for {self._pn(self.consent_player_pid)} 2FA")
            txt = self._render_player_colored_line(self.font_rule_bold, msg, HIGHLIGHT)
            layer = pygame.Surface((txt.get_width(), txt.get_height()), pygame.SRCALPHA)
            layer.blit(txt, (0, 0))
            layer.set_alpha(alpha)
            x = self.btn_symbol_o.x + (self.btn_symbol_x.right - self.btn_symbol_o.x - txt.get_width()) // 2
            y = self.btn_symbol_o.y + (self.btn_symbol_o.height - txt.get_height()) // 2
            self.screen.blit(layer, (x, y))

        self._draw_feedback()
        self._draw_text_button(self.btn_restart, self._t("重新开始", "Restart"), active=True)
        self._draw_text_button(self.btn_exit_home, self._t("返回到主界面", "Back to Home"))

        if self.game_over:
            overlay = pygame.Surface((BOARD_SIZE * CELL_SIZE, u(92)), pygame.SRCALPHA)
            overlay.fill((6, 8, 15, 170))
            self.screen.blit(overlay, (self.board_x, self.board_y + BOARD_SIZE * CELL_SIZE // 2 - u(46)))
            txt = self.font.render(self.winner_text, True, HIGHLIGHT)
            self.screen.blit(txt, (self.board_x + (BOARD_SIZE * CELL_SIZE - txt.get_width()) // 2, self.board_y + BOARD_SIZE * CELL_SIZE // 2 - u(12)))

    def _draw_home(self):
        self._draw_q_button()
        u = self._u

        x = self.panel_x + u(20)
        y = u(72)
        t1 = self.font.render("欢迎来到", True, TEXT_COLOR)
        t2 = self.font_bold.render("「开开你的！」", True, HIGHLIGHT)
        self.screen.blit(t1, (x, y))
        self.screen.blit(t2, (x + t1.get_width() + u(4), y))

        y2 = u(108)
        e1 = self.font_small.render("Welcome to ", True, SUB_TEXT)
        e2 = self.font_small_italic_bold.render("Gotcha !", True, SUB_TEXT)
        self.screen.blit(e1, (x, y2))
        self.screen.blit(e2, (x + e1.get_width(), y2))

        sy = u(152)
        shake = self._readonly_shake_offset()
        mode_label = self.font_rule_bold.render(self._t("模式：", "Mode: "), True, TEXT_COLOR)
        mode_value = self.font_rule.render(self._mode_short(), True, SUB_TEXT)
        self.screen.blit(mode_label, (x, sy))
        self.screen.blit(mode_value, (x + mode_label.get_width(), sy))
        t_time = self.font_rule_bold.render(self._t("时间：", "Time: "), True, TEXT_COLOR)
        t_val = self.font_rule.render(f"{self.turn_time_limit} s", True, SUB_TEXT)
        self.screen.blit(t_time, (x, sy + u(24)))
        self.screen.blit(t_val, (x + t_time.get_width(), sy + u(24)))
        self._draw_status_option(x + shake, sy + u(56), not self.option_disable_chat, self._t("聊天框", "Chat Box"), readonly=True)
        self._draw_status_option(x + u(188) + shake, sy + u(56), not self.option_disable_mic, self._t("麦克风", "Voice Chat"), readonly=True)
        self._draw_status_option(x + shake, sy + u(80), self.option_center_first, self._t("经典开局", "Classic Start"), readonly=True)
        self._draw_status_option(x + u(188) + shake, sy + u(80), self.option_symbol_alternate, self._t("正弦波", "Sine Wave"), readonly=True)

        self._draw_text_button(self.btn_home_start, self._t("开始", "Start"), active=False)
        self._draw_text_button(self.btn_home_mode, self._t("进阶模式", "Advanced Modes"))
        self._draw_text_button(self.btn_home_option, self._t("自定义选项", "Custom Options"))
        self._draw_text_button(self.btn_home_english, "中文" if self.english_mode else "English", active=False)

        ver = self.font_rule.render("v 0.1 ( beta )", True, SUB_TEXT)
        self.screen.blit(ver, (WINDOW_WIDTH - ver.get_width() - u(12), WINDOW_HEIGHT - ver.get_height() - u(8)))

    def _draw_mode_menu(self):
        self._draw_q_button()
        u = self._u
        self.screen.blit(self.font_mid.render(self._t("进阶模式", "Advanced Modes"), True, TEXT_COLOR), (self.panel_x + u(20), u(104)))

        mx, my = pygame.mouse.get_pos()
        hover_text = ""
        adv3_rect = None

        for rect, mode, _ in self.mode_btns:
            if mode == MODE_ADV3:
                adv3_rect = rect
                continue

            self._draw_text_button(rect, self._mode_menu_label(mode), active=(self.mode == mode))
            if rect.collidepoint(mx, my):
                if self.english_mode and mode in MODE_HOVER_RULES_EN:
                    hover_text = MODE_HOVER_RULES_EN[mode]
                elif mode in MODE_HOVER_RULES:
                    hover_text = MODE_HOVER_RULES[mode]

        if adv3_rect is not None:
            hover_adv3 = adv3_rect.collidepoint(mx, my)
            self.adv3_label_shift += ((1.0 if hover_adv3 else 0.0) - self.adv3_label_shift) * 0.24
            pressed_adv3 = self._is_button_pressed(adv3_rect)
            base_fill = (76, 104, 166) if self.mode != MODE_ADV3 else (111, 152, 244)
            base_border = HIGHLIGHT if self.mode == MODE_ADV3 else (126, 156, 218)
            if pressed_adv3:
                base_fill = (58, 80, 128)
                base_border = (104, 132, 186)
            pygame.draw.rect(self.screen, base_fill, adv3_rect, border_radius=8)
            pygame.draw.rect(self.screen, base_border, adv3_rect, 2, border_radius=8)
            dx = 1 if pressed_adv3 else 0
            dy = 1 if pressed_adv3 else 0

            label = self.font_small.render(self._t("进阶 3 - 暗黑心理学", "Advanced 3 - Masquerade"), True, TEXT_COLOR)
            scale = self._button_text_scale("btn_adv3_main", hover_adv3)
            centered_x = adv3_rect.centerx
            left_x = adv3_rect.x + 12 + label.get_width() // 2
            cx = int(round(centered_x + (left_x - centered_x) * self.adv3_label_shift)) + dx
            cy = adv3_rect.centery + dy
            self._blit_scaled_center(label, (cx, cy), scale)

            if hover_adv3:

                mini_w = self._u(34)
                gap = self._u(6)
                self.btn_adv3_o = pygame.Rect(adv3_rect.right - (mini_w * 2 + gap + self._u(8)), adv3_rect.y + self._u(4), mini_w, adv3_rect.height - self._u(8))
                self.btn_adv3_x = pygame.Rect(adv3_rect.right - (mini_w + self._u(8)), adv3_rect.y + self._u(4), mini_w, adv3_rect.height - self._u(8))

                self._draw_text_button(self.btn_adv3_o, "O", active=self.first_round_symbol_choice == "O", disabled=self.first_round_symbol_choice == "X")
                self._draw_text_button(self.btn_adv3_x, "X", active=self.first_round_symbol_choice == "X", disabled=self.first_round_symbol_choice == "O")
                hover_text = MODE_HOVER_RULES_EN[MODE_ADV3] if self.english_mode else MODE_HOVER_RULES[MODE_ADV3]
            else:
                self.btn_adv3_o = pygame.Rect(0, 0, 0, 0)
                self.btn_adv3_x = pygame.Rect(0, 0, 0, 0)

        self.screen.blit(self.font_rule.render(self._t("进阶模式仅能选择其中一个。", "Only one advanced mode can be selected."), True, HIGHLIGHT), (self.panel_x + u(20), u(376)))
        self._draw_hover_hint_panel_fade(hover_text, height=130)

        self._draw_text_button(self.btn_mode_back, self._t("返回到主界面", "Back to Home"))

    def _draw_checkbox(self, rect: pygame.Rect, checked: bool, text: str, y_offset: int = 0, scale: float = 1.0):
        u = self._u
        bw = max(14, int(round(rect.width * scale)))
        bh = max(14, int(round(rect.height * scale)))
        moved = pygame.Rect(0, 0, bw, bh)
        moved.centerx = rect.centerx
        moved.centery = rect.centery + y_offset
        pygame.draw.rect(self.screen, (62, 78, 115), moved, border_radius=3)
        pygame.draw.rect(self.screen, (132, 158, 213), moved, 2, border_radius=3)
        if checked:
            pygame.draw.line(self.screen, HIGHLIGHT, (moved.x + int(bw * 0.2), moved.y + int(bh * 0.55)), (moved.x + int(bw * 0.45), moved.y + int(bh * 0.8)), 2)
            pygame.draw.line(self.screen, HIGHLIGHT, (moved.x + int(bw * 0.45), moved.y + int(bh * 0.8)), (moved.x + int(bw * 0.82), moved.y + int(bh * 0.2)), 2)
        render_text = text
        txt = self.font_rule.render(render_text, True, TEXT_COLOR)
        max_w = u(350)
        if txt.get_width() > max_w:
            while len(render_text) > 3:
                render_text = render_text[:-1]
                candidate = render_text + "..."
                t = self.font_rule.render(candidate, True, TEXT_COLOR)
                if t.get_width() <= max_w:
                    txt = t
                    break
        self.screen.blit(txt, (moved.x + u(24), moved.y - u(1)))

    def _draw_option_menu(self):
        self._draw_q_button()
        u = self._u
        self.screen.blit(self.font_mid.render(self._t("自定义选项", "Custom Options"), True, TEXT_COLOR), (self.panel_x + u(20), u(126)))

        mx, my = pygame.mouse.get_pos()
        hov1 = pygame.Rect(self.chk_opt1.x, self.chk_opt1.y - u(2), u(380), u(22)).collidepoint(mx, my)
        hov2 = pygame.Rect(self.chk_opt2.x, self.chk_opt2.y - u(2), u(380), u(22)).collidepoint(mx, my)
        hov3 = pygame.Rect(self.chk_opt3.x, self.chk_opt3.y - u(2), u(380), u(22)).collidepoint(mx, my)
        hov4 = pygame.Rect(self.chk_opt4.x, self.chk_opt4.y - u(2), u(380), u(22)).collidepoint(mx, my)
        hov5 = pygame.Rect(self.chk_opt5.x, self.chk_opt5.y - u(2), u(380), u(22)).collidepoint(mx, my)

        self._draw_checkbox(self.chk_opt1, self.option_disable_chat, self._t("转人工：禁用聊天框", "Speaking is fun ! : Disable chat boxes"), self._checkbox_bounce_offset(1), self._checkbox_hover_scale_value(1, hov1))
        self._draw_checkbox(self.chk_opt2, self.option_disable_mic, self._t("请输入文本：禁用麦克风", "Typing is fun ! : Disable voice chat"), self._checkbox_bounce_offset(2), self._checkbox_hover_scale_value(2, hov2))
        self._draw_checkbox(self.chk_opt3, self.option_disable_both, self._t("已严肃下棋：禁用聊天框和麦克风", "Muting is fun ( Probably ? ) : Disable both"), self._checkbox_bounce_offset(3), self._checkbox_hover_scale_value(3, hov3))
        self._draw_checkbox(self.chk_opt4, self.option_center_first, self._t("经典开局：首子居中", "Classic Start: first piece at center"), self._checkbox_bounce_offset(4), self._checkbox_hover_scale_value(4, hov4))
        self._draw_checkbox(self.chk_opt5, self.option_symbol_alternate, self._t("正弦波：符号交替", "Sine Wave: marks alternate"), self._checkbox_bounce_offset(5), self._checkbox_hover_scale_value(5, hov5))

        self.screen.blit(self.font_rule.render(self._t("时间吞噬者：每名玩家可用时间", "Time Eater: time per player"), True, TEXT_COLOR), (self.panel_x + u(44), u(308)))

        pygame.draw.rect(self.screen, (68, 82, 116), self.slider_rect, border_radius=5)
        ratio = (self.turn_time_limit_visual - TIME_MIN) / (TIME_MAX - TIME_MIN)
        ratio = max(0.0, min(1.0, ratio))
        knob_x = self.slider_rect.x + int(ratio * self.slider_rect.width)
        pygame.draw.circle(self.screen, HIGHLIGHT, (knob_x, self.slider_rect.centery), u(8))
        self.screen.blit(self.font_rule.render(f"{self.turn_time_limit} s", True, TEXT_COLOR), (self.slider_rect.right + u(16), self.slider_rect.y - u(8)))

        opt1_area = pygame.Rect(self.chk_opt1.x, self.chk_opt1.y - u(2), u(380), u(22))
        opt2_area = pygame.Rect(self.chk_opt2.x, self.chk_opt2.y - u(2), u(380), u(22))
        opt3_area = pygame.Rect(self.chk_opt3.x, self.chk_opt3.y - u(2), u(380), u(22))
        opt4_area = pygame.Rect(self.chk_opt4.x, self.chk_opt4.y - u(2), u(380), u(22))
        opt5_area = pygame.Rect(self.chk_opt5.x, self.chk_opt5.y - u(2), u(380), u(22))
        slider_area = pygame.Rect(self.slider_rect.x - u(12), self.slider_rect.y - u(26), self.slider_rect.width + u(140), u(40))

        hover_text = ""
        if opt1_area.collidepoint(mx, my):
            hover_text = OPTION_HOVER_RULES_EN[1] if self.english_mode else OPTION_HOVER_RULES[1]
        elif opt2_area.collidepoint(mx, my):
            hover_text = OPTION_HOVER_RULES_EN[2] if self.english_mode else OPTION_HOVER_RULES[2]
        elif opt3_area.collidepoint(mx, my):
            hover_text = OPTION_HOVER_RULES_EN[3] if self.english_mode else OPTION_HOVER_RULES[3]
        elif opt4_area.collidepoint(mx, my):
            hover_text = OPTION_HOVER_RULES_EN[4] if self.english_mode else OPTION_HOVER_RULES[4]
        elif opt5_area.collidepoint(mx, my):
            hover_text = OPTION_HOVER_RULES_EN[5] if self.english_mode else OPTION_HOVER_RULES[5]
        elif slider_area.collidepoint(mx, my):
            hover_text = OPTION_HOVER_RULES_EN[6] if self.english_mode else OPTION_HOVER_RULES[6]

        self.screen.blit(self.font_rule.render(self._t("自定义选项可以同时开启多个，开启后对任意模式均生效。", "Multiple options can be enabled and apply to all modes."), True, HIGHLIGHT), (self.panel_x + u(20), u(376)))
        self._draw_hover_hint_panel_fade(hover_text, height=110)

        self._draw_text_button(self.btn_opt_back, self._t("返回到主界面", "Back to Home"))

    def _draw_reveal(self):
        self._draw_q_button()
        u = self._u
        self.screen.blit(self.font_mid.render(self._t("按住对应按钮查看你的阵营", "Hold your button to view your team"), True, TEXT_COLOR), (self.panel_x + u(20), u(72)))
        viewed_txt = self.font_rule.render(self._t(f"已查看：{len(self.reveal_viewed)}/4", f"Viewed: {len(self.reveal_viewed)}/4"), True, SUB_TEXT)
        self.screen.blit(viewed_txt, (self.panel_x + u(20), u(104)))

        mapping = [
            (1, self.btn_reveal_p1),
            (2, self.btn_reveal_p2),
            (3, self.btn_reveal_p3),
            (4, self.btn_reveal_p4),
        ]

        for pid, rect in mapping:
            pl = self.players[pid - 1]
            active = self.reveal_hold_pid == pid and self.left_mouse_down

            fill = (74, 104, 166) if not active else (142, 170, 235)
            border = pl.color
            txt_color = pl.color if not active else (10, 14, 24)

            pygame.draw.rect(self.screen, fill, rect, border_radius=10)
            pygame.draw.rect(self.screen, border, rect, 2, border_radius=10)

            txt = self.font_mid.render(self._pn(pid), True, txt_color)
            self.screen.blit(txt, (rect.x + (rect.width - txt.get_width()) // 2, rect.y + (rect.height - txt.get_height()) // 2))

        start_enabled = len(self.reveal_viewed) == 4
        self._draw_text_button(self.btn_reveal_start, self._t("查看完毕，开始游戏", "Done Viewing, Start Game"), active=start_enabled, disabled=not start_enabled)
        self._draw_text_button(self.btn_reveal_home, self._t("返回到主界面", "Back to Home"))

        if self.reveal_hint_alpha > 0.01 and self.reveal_hold_pid is not None:
            pl = self.players[self.reveal_hold_pid - 1]
            camp = pl.camp
            panel_w = u(270)
            panel_h = u(82)
            mx, my = pygame.mouse.get_pos()
            px = mx + u(16)
            py = my + u(14)
            if px + panel_w > WINDOW_WIDTH - u(8):
                px = mx - panel_w - u(16)
            if py + panel_h > WINDOW_HEIGHT - u(8):
                py = my - panel_h - u(14)
            px = max(u(8), min(px, WINDOW_WIDTH - panel_w - u(8)))
            py = max(u(8), min(py, WINDOW_HEIGHT - panel_h - u(8)))
            panel = pygame.Rect(px, py, panel_w, panel_h)

            layer = pygame.Surface((panel.width, panel.height), pygame.SRCALPHA)
            alpha = int(255 * max(0.0, min(1.0, self.reveal_hint_alpha)))
            pygame.draw.rect(layer, (34, 42, 66, alpha), (0, 0, panel.width, panel.height), border_radius=10)
            pygame.draw.rect(layer, (104, 132, 190, alpha), (0, 0, panel.width, panel.height), 2, border_radius=10)
            self.screen.blit(layer, panel.topleft)

            t_title = self.font_rule.render(self._t(f"{self._pn(pl.pid)} 的阵营", f"{self._pn(pl.pid)} team"), True, SUB_TEXT)
            self.screen.blit(t_title, (panel.x + u(12), panel.y + u(9)))

            sym = "O" if camp == "O" else "X"
            camp_text = self._t("圈 (O)", "Circle (O)") if camp == "O" else self._t("叉 (X)", "Cross (X)")
            t2 = self.font_rule_bold.render(camp_text, True, pl.color)
            self.screen.blit(t2, (panel.x + u(12), panel.y + u(44) - t2.get_height() // 2))

            symbol_x = panel.right - u(54)
            center_y = panel.centery
            self._draw_symbol(self.screen, sym, (symbol_x, center_y), pl.color, u(24), max(5, u(6)))

    def _draw_credits(self):
        self._draw_q_button()
        u = self._u

        left_x = self.panel_x + u(20)
        top_y = u(44)
        self.screen.blit(self.font_mid_bold.render("制作人员", True, HIGHLIGHT), (left_x, top_y))

        rows = [
            ("规则构思、方案设想、环境搭建、测试验证、桌游实现、进阶开发、文档编辑、后期更新与维护", "Tito_Grumm"),
            ("代码编写", "GPT-5.3-Codex"),
            ("规则优化、测试验证、桌游实现", "七七"),
            ("规则优化、测试验证、桌游实现", "羊村你喜哥"),
            ("规则优化、测试验证、桌游实现", "Olio_Ert"),
            ("测试验证、桌游实现", "野俟蔓草"),
        ]

        table_x = left_x - u(10)
        table_y = top_y + u(28)
        table_w = min(PANEL_WIDTH - u(24), u(620))
        name_col_w = min(u(170), max(u(120), int(table_w * 0.3)))
        duty_col_w = table_w - name_col_w - u(20)
        row_gap = u(4)
        line_h = max(self.font_rule.get_height() + u(3), u(18))

        row_defs: List[Tuple[List[str], str, int]] = []
        for duty, name in rows:
            duty_lines = self._wrap_text(duty, self.font_rule, max(u(80), duty_col_w - u(16)))
            row_h = max(u(28), len(duty_lines) * line_h)
            row_defs.append((duty_lines, name, row_h))

        table_h = sum(h for _, _, h in row_defs) + row_gap * (len(row_defs) - 1) + u(12)
        table_rect = pygame.Rect(table_x, table_y, table_w, table_h)
        pygame.draw.rect(self.screen, (28, 35, 52), table_rect, border_radius=10)
        pygame.draw.rect(self.screen, (96, 122, 176), table_rect, 1, border_radius=10)

        split_x = table_rect.right - name_col_w - u(10)
        pygame.draw.line(self.screen, (96, 122, 176), (split_x, table_rect.y + u(4)), (split_x, table_rect.bottom - u(4)), 1)

        yy = table_rect.y + u(6)
        for idx, (duty_lines, name, row_h) in enumerate(row_defs):
            duty_cell_x = table_rect.x + u(8)
            duty_cell_w = split_x - duty_cell_x - u(8)
            duty_y = yy + (row_h - len(duty_lines) * line_h) // 2
            for line in duty_lines:
                img = self.font_rule.render(line, True, SUB_TEXT)
                dx = duty_cell_x + max(0, (duty_cell_w - img.get_width()) // 2)
                self.screen.blit(img, (dx, duty_y))
                duty_y += line_h

            name_img = self.font_rule_bold.render(name, True, TEXT_COLOR)
            name_cell_x = split_x + u(1)
            name_cell_w = table_rect.right - name_cell_x - u(8)
            name_x = name_cell_x + max(0, (name_cell_w - name_img.get_width()) // 2)
            name_y = yy + (row_h - name_img.get_height()) // 2
            self.screen.blit(name_img, (name_x, name_y))

            yy += row_h
            if idx < len(row_defs) - 1:
                yy += row_gap
                pygame.draw.line(self.screen, (80, 98, 140), (table_rect.x + u(6), yy - row_gap // 2), (table_rect.right - u(6), yy - row_gap // 2), 1)

        y = table_rect.bottom + u(8)
        thanks_lines = [
            "同时感谢 @羊村你喜哥 和 @七七 带来的彩色笔，",
            "以及《只只大冒险》主创之一 @Jing 老师提供的",
            "课程平台和试玩反馈！",
        ]
        for line in thanks_lines:
            self.screen.blit(self.font_rule.render(line, True, SUB_TEXT), (left_x, y))
            y += line_h
        y += u(6)

        box_h = max(u(36), (WINDOW_HEIGHT - BOARD_MARGIN) - y)
        box = pygame.Rect(table_x, y, table_w, box_h)
        pygame.draw.rect(self.screen, (28, 35, 52), box, border_radius=10)
        pygame.draw.rect(self.screen, (96, 122, 176), box, 1, border_radius=10)

        ty = box.y + u(10)
        self.screen.blit(self.font_mid_bold.render("致敬游戏", True, HIGHLIGHT), (box.x + u(10), ty))
        ty += u(30)

        def draw_entry(name: str, desc_lines: List[str], yy: int) -> int:
            name_img = self.font_rule_bold.render(name, True, TEXT_COLOR)
            self.screen.blit(name_img, (box.x + u(10), yy))
            yy += u(24)
            for raw in desc_lines:
                lines = self._wrap_text(raw, self.font_rule, box.width - u(24))
                for line in lines:
                    if yy > box.bottom - u(18):
                        return yy
                    self.screen.blit(self.font_rule.render(line, True, SUB_TEXT), (box.x + u(10), yy))
                    yy += line_h
            return yy + u(6)

        ty = draw_entry(
            "猛兽派对 / Party Animals",
            [
                "「猛兽摸鱼」和「吹牛俱乐部」可能不是原创，",
                "但我正是在小屋里接触到「骗」和「开」的玩法的！",
            ],
            ty,
        )
        ty = draw_entry("Inscryption / 邪恶铭刻", ["最喜欢的游戏！"], ty)
        draw_entry(
            "Slay the Spire / 杀戮尖塔",
            ["借鉴了这款游戏和《邪恶铭刻》中的「进阶」创意！"],
            ty,
        )

    # ---------- 规则浮层 ----------
    def _draw_rules_overlay(self):
        u = self._u
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 10, 18, 220))

        panel = pygame.Rect(u(40), u(30), WINDOW_WIDTH - u(80), WINDOW_HEIGHT - u(60))
        pygame.draw.rect(overlay, (25, 33, 50), panel, border_radius=12)
        pygame.draw.rect(overlay, (116, 146, 210), panel, 2, border_radius=12)

        overlay.blit(self.font_mid.render(self._t("游戏规则 / Game Rules", "Game Rules"), True, TEXT_COLOR), (panel.x + u(16), panel.y + u(12)))

        def draw_overlay_button(rect: pygame.Rect, text: str, disabled: bool = False):
            pressed = self._is_button_pressed(rect)
            sx = self._disabled_button_shake_offset(rect) if disabled else 0
            drect = rect.move(sx, 0)
            if disabled:
                fill, border, color = (56, 62, 78), (76, 86, 110), DISABLED_TEXT
            else:
                fill, border, color = (76, 104, 166), (126, 156, 218), TEXT_COLOR
                if pressed:
                    fill, border = (58, 80, 128), (104, 132, 186)
            pygame.draw.rect(overlay, fill, drect, border_radius=8)
            pygame.draw.rect(overlay, border, drect, 2, border_radius=8)
            img = self.font_small.render(text, True, color)
            dx = 1 if pressed and not disabled else 0
            dy = 1 if pressed and not disabled else 0
            mx, my = pygame.mouse.get_pos()
            key = f"overlay:{drect.x},{drect.y},{drect.width},{drect.height}:{text}"
            scale = self._button_text_scale(key, drect.collidepoint(mx, my))
            img, scale = self._fit_button_text(self.font_small, text, color, max(10, drect.width - 18), scale)

            if abs(scale - 1.0) < 0.01:
                overlay.blit(img, (drect.x + (drect.width - img.get_width()) // 2 + dx, drect.y + (drect.height - img.get_height()) // 2 + dy))
            else:
                nw = max(1, int(round(img.get_width() * scale)))
                nh = max(1, int(round(img.get_height() * scale)))
                scaled = pygame.transform.scale(img, (nw, nh))
                overlay.blit(scaled, (drect.centerx - nw // 2 + dx, drect.centery - nh // 2 + dy))

        self.btn_rule_close = pygame.Rect(panel.right - u(92), panel.y + u(10), u(76), u(30))
        draw_overlay_button(self.btn_rule_close, self._t("返回", "Back"))

        content = pygame.Rect(panel.x + u(16), panel.y + u(50), panel.width - u(32), panel.height - u(100))
        lines = self._wrap_rules_cached(content.width)
        pages = self._paginate_rules_cached(lines, content.height)
        self.rules_page = max(0, min(self.rules_page, len(pages) - 1))
        self.rules_page_display += (float(self.rules_page) - self.rules_page_display) * 0.42
        if abs(self.rules_page_display - float(self.rules_page)) < 0.002:
            self.rules_page_display = float(self.rules_page)

        p = max(0.0, min(float(len(pages) - 1), self.rules_page_display))
        page_idx = int(math.floor(p))
        next_idx = min(len(pages) - 1, page_idx + 1)
        frac = p - page_idx

        surface_key = (id(pages), content.width, content.height)
        if self._rules_page_surface_key != surface_key or len(self._rules_page_surfaces) != len(pages):
            self._rules_page_surface_key = surface_key
            self._rules_page_surfaces = []
            for pg in pages:
                surf = pygame.Surface((content.width, content.height), pygame.SRCALPHA)
                yy = 0
                for text, is_title in pg:
                    h = self._rule_line_height(text, is_title)
                    if text != "":
                        font = self.font_mid if is_title else self.font_rule
                        color = HIGHLIGHT if is_title else SUB_TEXT
                        surf.blit(font.render(text, True, color), (0, yy))
                    yy += h
                self._rules_page_surfaces.append(surf)

        cur_page = self._rules_page_surfaces[page_idx]
        next_page = self._rules_page_surfaces[next_idx]

        prev_clip = overlay.get_clip()
        overlay.set_clip(content)
        overlay.blit(cur_page, (content.x - int(frac * content.width), content.y))
        if next_idx != page_idx:
            overlay.blit(next_page, (content.x + int((1.0 - frac) * content.width), content.y))
        overlay.set_clip(prev_clip)

        self.btn_rule_prev = pygame.Rect(panel.x + u(16), panel.bottom - u(40), u(92), u(28))
        self.btn_rule_next = pygame.Rect(panel.right - u(108), panel.bottom - u(40), u(92), u(28))

        is_first = self.rules_page <= 0
        is_last = self.rules_page >= len(pages) - 1
        draw_overlay_button(self.btn_rule_prev, self._t("上一页", "Prev"), disabled=is_first)
        draw_overlay_button(self.btn_rule_next, self._t("下一页", "Next"), disabled=is_last)

        pi = self.font_rule.render(f"{self.rules_page + 1}/{len(pages)}", True, TEXT_COLOR)
        overlay.blit(pi, (panel.centerx - pi.get_width() // 2, panel.bottom - u(34)))

        overlay.set_alpha(int(255 * max(0.0, min(1.0, self.rules_overlay_alpha))))
        self.screen.blit(overlay, (0, 0))

    def _wrap_rules_cached(self, width: int) -> List[Tuple[str, bool]]:
        if width != self._rules_wrap_width_cached:
            self._rules_lines_cached = self._wrap_rules(width)
            self._rules_wrap_width_cached = width
            self._rules_pages_height_cached = -1
            self._rules_page_surface_key = None
            self._rules_page_surfaces = []
        return self._rules_lines_cached

    def _paginate_rules_cached(self, lines: List[Tuple[str, bool]], height: int) -> List[List[Tuple[str, bool]]]:
        if height != self._rules_pages_height_cached or not self._rules_pages_cached:
            self._rules_pages_cached = self._paginate_rules(lines, height)
            self._rules_pages_height_cached = height
            self._rules_page_surface_key = None
            self._rules_page_surfaces = []
        return self._rules_pages_cached

    def _wrap_rules(self, width: int) -> List[Tuple[str, bool]]:
        out: List[Tuple[str, bool]] = []
        src = RULES_TEXT_EN if self.english_mode else RULES_TEXT
        for raw in src:
            if raw == "":
                out.append(("", False))
                continue
            is_title = raw.startswith("开开你的！") or raw.startswith("Gotcha") or (len(raw) >= 2 and raw[0].isdigit() and raw[1] == ".")
            font = self.font_mid if is_title else self.font_rule
            out.extend([(x, is_title) for x in self._wrap_text_smart(raw, font, width)])
        return out

    def _rule_line_height(self, text: str, is_title: bool) -> int:
        u = self._u
        if text == "":
            return max(u(12), self.font_rule.get_height() // 2)
        if is_title:
            return self.font_mid.get_height() + u(8)
        return self.font_rule.get_height() + u(7)

    def _paginate_rules(self, lines: List[Tuple[str, bool]], height: int) -> List[List[Tuple[str, bool]]]:
        pages: List[List[Tuple[str, bool]]] = []
        page: List[Tuple[str, bool]] = []
        used = 0
        for text, is_title in lines:
            h = self._rule_line_height(text, is_title)
            if page and used + h > height:
                pages.append(page)
                page = []
                used = 0
            page.append((text, is_title))
            used += h
        if page:
            pages.append(page)
        return pages if pages else [[(self._t("暂无规则", "No rules"), False)]]

    # ---------- 事件 ----------
    def _handle_rules_click(self, mx: int, my: int):
        total_pages = len(self._rules_pages_cached) if self._rules_pages_cached else (self.rules_page + 1)
        if self.btn_rule_close.collidepoint(mx, my):
            self.show_rules = False
        elif self.btn_rule_prev.collidepoint(mx, my) and self.rules_page > 0:
            self.rules_page_display = float(self.rules_page)
            self.rules_page -= 1
        elif self.btn_rule_next.collidepoint(mx, my) and self.rules_page < total_pages - 1:
            self.rules_page_display = float(self.rules_page)
            self.rules_page += 1

    def _update_slider(self, mx: int):
        ratio = (mx - self.slider_rect.x) / max(1, self.slider_rect.width)
        ratio = max(0.0, min(1.0, ratio))
        self.turn_time_limit = int(round(TIME_MIN + ratio * (TIME_MAX - TIME_MIN)))

    def _handle_home_click(self, mx: int, my: int):
        if self.btn_q.collidepoint(mx, my):
            self.show_rules = True
            self.rules_page = 0
            return
        if self.btn_home_mode.collidepoint(mx, my):
            self.app_state = AppState.MODE_MENU
            return
        if self.btn_home_option.collidepoint(mx, my):
            self.app_state = AppState.OPTION_MENU
            return
        if self.btn_home_start.collidepoint(mx, my):
            self._new_players()
            self.reveal_hold_pid = None
            self.reveal_viewed.clear()
            self.app_state = AppState.REVEAL
            return
        if self.btn_home_credits.collidepoint(mx, my):
            self.app_state = AppState.CREDITS
            return

    def _handle_mode_menu_click(self, mx: int, my: int):
        if self.btn_q.collidepoint(mx, my):
            self.show_rules = True
            self.rules_page = 0
            return

        if self.btn_adv3_o.collidepoint(mx, my):
            self.first_round_symbol_choice = "O"
            return
        if self.btn_adv3_x.collidepoint(mx, my):
            self.first_round_symbol_choice = "X"
            return

        for rect, m, _ in self.mode_btns:
            if rect.collidepoint(mx, my):
                self.mode = m
                return
        if self.btn_mode_back.collidepoint(mx, my):
            self.app_state = AppState.HOME

    def _handle_option_menu_click(self, mx: int, my: int):
        u = self._u
        if self.btn_q.collidepoint(mx, my):
            self.show_rules = True
            self.rules_page = 0
            return

        if self.chk_opt1.collidepoint(mx, my):
            self.option_disable_chat = not self.option_disable_chat
            self._sync_disable_options()
            self._trigger_checkbox_bounce(1)
            self._play_sfx("check")
            return

        if self.chk_opt2.collidepoint(mx, my):
            self.option_disable_mic = not self.option_disable_mic
            self._sync_disable_options()
            self._trigger_checkbox_bounce(2)
            self._play_sfx("check")
            return

        if self.chk_opt3.collidepoint(mx, my):
            self.option_disable_both = not self.option_disable_both
            if self.option_disable_both:
                self.option_disable_chat = True
                self.option_disable_mic = True
            else:
                self.option_disable_chat = False
                self.option_disable_mic = False
            self._sync_disable_options()
            self._trigger_checkbox_bounce(3)
            self._play_sfx("check")
            return

        if self.chk_opt4.collidepoint(mx, my):
            self.option_center_first = not self.option_center_first
            self._trigger_checkbox_bounce(4)
            self._play_sfx("check")
            return

        if self.chk_opt5.collidepoint(mx, my):
            self.option_symbol_alternate = not self.option_symbol_alternate
            self._trigger_checkbox_bounce(5)
            self._play_sfx("check")
            return

        slider_hit = pygame.Rect(self.slider_rect.x - u(8), self.slider_rect.y - u(8), self.slider_rect.width + u(16), u(26))
        if slider_hit.collidepoint(mx, my):
            self.slider_drag = True
            self._update_slider(mx)
            self._play_sfx("tick", throttle_ms=35)
            return

        if self.btn_opt_back.collidepoint(mx, my):
            self.app_state = AppState.HOME

    def _handle_reveal_click(self, mx: int, my: int):
        if self.btn_q.collidepoint(mx, my):
            self.show_rules = True
            self.rules_page = 0
            return

        if self.btn_reveal_home.collidepoint(mx, my):
            self.app_state = AppState.HOME
            self.reveal_hold_pid = None
            return

        if self.btn_reveal_start.collidepoint(mx, my) and len(self.reveal_viewed) == 4:
            self.app_state = AppState.GAME
            self._prepare_game_from_reveal()
            return

        player_btns = {
            1: self.btn_reveal_p1,
            2: self.btn_reveal_p2,
            3: self.btn_reveal_p3,
            4: self.btn_reveal_p4,
        }
        for pid, rect in player_btns.items():
            if rect.collidepoint(mx, my):
                self.reveal_hold_pid = pid
                self.reveal_viewed.add(pid)
                self._play_sfx("click")
                return

    def _handle_credits_click(self, mx: int, my: int):
        if self.btn_q.collidepoint(mx, my):
            self.show_rules = True
            self.rules_page = 0
            return

    def _handle_game_click(self, mx: int, my: int):
        self._layout_game_panel_controls()
        if self.btn_restart.collidepoint(mx, my):
            self._restart_with_new_assignment()
            return
        if self.btn_exit_home.collidepoint(mx, my):
            self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
            self.pending_piece = None
            self.pending_lines.clear()
            self.last_confirmed_cell = None
            self.opened_line_cells = None
            self.waiting_line_cells = None
            self.rejected_line_cells = None
            self.rejected_line_alpha = 0.0
            self.consent_status_text = ""
            self.app_state = AppState.HOME
            return
        if self.btn_q.collidepoint(mx, my):
            self.show_rules = True
            self.rules_page = 0
            return
        if self.game_over:
            return

        if self.open_waiting_consent:
            action_items, _, _ = self._action_buttons_view()
            for rect, kind, _ in action_items:
                if rect.collidepoint(mx, my):
                    self.touched_this_turn = True
                    if kind == "agree" and self.chosen_line is not None:
                        cp = self.consent_player_pid if self.consent_player_pid is not None else self.current_player().pid
                        self.consent_status_text = self._t(f"{self._pn(cp)} 已同意开盒。", f"{self._pn(cp)} agreed to open.")
                        self._add_feedback(self.consent_status_text, HIGHLIGHT, bold=True, player_pid=cp)
                        self._evaluate_open_line(self.chosen_line)
                    elif kind == "reject":
                        cp = self.consent_player_pid if self.consent_player_pid is not None else self.current_player().pid
                        msg = self._t(f"{self._pn(cp)} 不同意开盒，该四连作废。", f"{self._pn(cp)} rejected opening, this VFR is void.")
                        if self.waiting_line_cells:
                            self.rejected_line_cells = list(self.waiting_line_cells)
                            self.rejected_line_alpha = 1.0
                        self._commit_pending_without_open(msg)
                    return
            return

        p = self.current_player()
        avail = self._available_symbols(p)

        if self.btn_symbol_o.collidepoint(mx, my) and "O" in avail:
            self.selected_symbol = "O"
            if self.pending_piece:
                self.pending_piece.symbol = "O"
                self.pending_lines = self._detect_new_lines_for_pending(self.pending_piece)
            self.touched_this_turn = True
            self._play_sfx("click")
            return

        if self.btn_symbol_x.collidepoint(mx, my) and "X" in avail:
            self.selected_symbol = "X"
            if self.pending_piece:
                self.pending_piece.symbol = "X"
                self.pending_lines = self._detect_new_lines_for_pending(self.pending_piece)
            self.touched_this_turn = True
            self._play_sfx("click")
            return

        action_items, _, _ = self._action_buttons_view()
        for rect, kind, payload in action_items:
            if rect.collidepoint(mx, my):
                self.touched_this_turn = True

                if kind == "confirm" and self.pending_piece is not None:
                    pp = self.pending_piece
                    self._commit_pending_without_open(
                        self._t(
                            f"{self._pn(pp.owner_pid)} 确认落子于 {self._coord(pp.row, pp.col)}。",
                            f"{self._pn(pp.owner_pid)} confirmed placement at {self._coord(pp.row, pp.col)}.",
                        )
                    )
                    return

                if kind == "no_open":
                    pid = self.current_player().pid
                    pp = self.pending_piece
                    self._commit_pending_without_open(
                        self._t(
                            f"{self._pn(pid)} 确认落子于 {self._coord(pp.row, pp.col)}，选择不开盒。",
                            f"{self._pn(pid)} confirmed placement at {self._coord(pp.row, pp.col)} and chose not to open.",
                        )
                    )
                    return

                if kind == "open_line" and payload is not None:
                    line = self.pending_lines[payload]
                    if self._mode_at_least(MODE_ADV2):
                        owners = {self._owner_with_pending(r, c, self.pending_piece) for r, c in line.cells}
                        owners.discard(self.current_player().pid)
                        if not owners:
                            self._add_feedback(self._t("该四连无可验证对象，无法开盒。", "No valid verifier for this VFR. Cannot open."), SUB_TEXT)
                            return
                        self.chosen_line = line
                        self.consent_player_pid = sorted(list(owners))[0]
                        self.open_waiting_consent = True
                        self.waiting_line_cells = list(line.cells)
                        self.rejected_line_cells = None
                        self.rejected_line_alpha = 0.0
                        self.consent_status_text = ""
                        opener = self.current_player().pid
                        pp = self.pending_piece
                        self._add_feedback(
                            self._t(
                                f"{self._pn(opener)} 确认落子于 {self._coord(pp.row, pp.col)} 并发起开盒，等待 {self._pn(self.consent_player_pid)} 二次验证。",
                                f"{self._pn(opener)} confirmed placement at {self._coord(pp.row, pp.col)} and initiated opening, waiting for {self._pn(self.consent_player_pid)} 2FA.",
                            ),
                            HIGHLIGHT,
                            bold=True,
                        )
                    else:
                        pp = self.pending_piece
                        opener = self.current_player().pid
                        if pp is not None:
                            self._add_feedback(
                                self._t(
                                    f"{self._pn(opener)} 确认落子于 {self._coord(pp.row, pp.col)} 并开盒。",
                                    f"{self._pn(opener)} confirmed placement at {self._coord(pp.row, pp.col)} and opened.",
                                ),
                                HIGHLIGHT,
                                bold=True,
                                player_pid=opener,
                            )
                        self._evaluate_open_line(line)
                    return
                return

        cell = self._cell_from_mouse(mx, my)
        if cell is None:
            return
        r, c = cell
        if self.board[r][c] is not None:
            return

        if self.option_center_first and self._confirmed_count() == 0:
            center = BOARD_SIZE // 2
            if (r, c) != (center, center):
                return

        player = self.current_player()
        if self.pending_piece is None:
            self.pending_piece = PendingPiece(r, c, self.selected_symbol, player.pid)
        else:
            self.pending_piece.row = r
            self.pending_piece.col = c
            self.pending_piece.symbol = self.selected_symbol
            self.pending_piece.owner_pid = player.pid

        self.pending_lines = self._detect_new_lines_for_pending(self.pending_piece)
        self.touched_this_turn = True
        self._play_sfx("place")

    # ---------- 主循环 ----------
    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0

            if self.app_state == AppState.GAME:
                self._layout_game_panel_controls()

            self.turn_time_limit_visual += (float(self.turn_time_limit) - self.turn_time_limit_visual) * min(1.0, dt * 12.0)
            self.feedback_scroll_display += (self.feedback_scroll_target - self.feedback_scroll_display) * min(1.0, dt * 14.0)
            self.action_scroll_display += (self.action_scroll_target - self.action_scroll_display) * min(1.0, dt * 14.0)

            reveal_target = 1.0 if (self.app_state == AppState.REVEAL and self.reveal_hold_pid is not None and self.left_mouse_down) else 0.0
            self.reveal_hint_alpha += (reveal_target - self.reveal_hint_alpha) * min(1.0, dt * 12.0)
            if self.readonly_shake_elapsed < self.readonly_shake_duration:
                self.readonly_shake_elapsed += dt
            for k in self.checkbox_bounce_elapsed.keys():
                if self.checkbox_bounce_elapsed[k] < self.checkbox_bounce_duration:
                    self.checkbox_bounce_elapsed[k] += dt
            for k in list(self.disabled_button_shake_elapsed.keys()):
                self.disabled_button_shake_elapsed[k] += dt
                if self.disabled_button_shake_elapsed[k] >= self.disabled_button_shake_duration:
                    self.disabled_button_shake_elapsed.pop(k, None)

            target_rules_alpha = 1.0 if self.show_rules else 0.0
            self.rules_overlay_alpha += (target_rules_alpha - self.rules_overlay_alpha) * min(1.0, dt * 14.0)
            if self.rules_overlay_alpha < 0.01 and not self.show_rules:
                self.rules_page_display += (float(self.rules_page) - self.rules_page_display) * 0.2

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.left_mouse_down = True
                    mx, my = event.pos
                    self.pressed_button_rect = None

                    if (not self.show_rules) and self._handle_readonly_checkbox_click(mx, my):
                        continue

                    if self.app_state == AppState.GAME and self.action_thumb_rect.collidepoint(mx, my):
                        self.action_dragging = True
                        self.action_drag_offset = my - self.action_thumb_rect.y
                        continue

                    disabled_rects = self._disabled_button_rects()
                    if any(r.collidepoint(mx, my) for r in disabled_rects):
                        for r in disabled_rects:
                            if r.collidepoint(mx, my):
                                self._trigger_disabled_button_shake(r)
                                break
                        continue

                    if self._is_text_button_hit(mx, my):
                        self.pressed_button_rect = pygame.Rect(mx, my, 1, 1)
                        if self.show_rules:
                            if self.btn_rule_close.collidepoint(mx, my):
                                self.pressed_button_rect = self.btn_rule_close.copy()
                            elif self.btn_rule_prev.collidepoint(mx, my):
                                self.pressed_button_rect = self.btn_rule_prev.copy()
                            elif self.btn_rule_next.collidepoint(mx, my):
                                self.pressed_button_rect = self.btn_rule_next.copy()
                        elif self.btn_q.collidepoint(mx, my):
                            self.pressed_button_rect = self.btn_q.copy()
                        elif self.btn_home_credits.collidepoint(mx, my):
                            self.pressed_button_rect = self.btn_home_credits.copy()
                        elif self.app_state == AppState.HOME:
                            for rect in (self.btn_home_start, self.btn_home_mode, self.btn_home_option, self.btn_home_english):
                                if rect.collidepoint(mx, my):
                                    self.pressed_button_rect = rect.copy()
                                    break
                        elif self.app_state == AppState.MODE_MENU:
                            for rect, _, _ in self.mode_btns:
                                if rect.collidepoint(mx, my):
                                    self.pressed_button_rect = rect.copy()
                                    break
                            for rect in (self.btn_adv3_o, self.btn_adv3_x, self.btn_mode_back):
                                if rect.collidepoint(mx, my):
                                    self.pressed_button_rect = rect.copy()
                                    break
                        elif self.app_state == AppState.OPTION_MENU:
                            if self.btn_opt_back.collidepoint(mx, my):
                                self.pressed_button_rect = self.btn_opt_back.copy()
                        elif self.app_state == AppState.REVEAL:
                            for rect in (self.btn_reveal_start, self.btn_reveal_home):
                                if rect.collidepoint(mx, my):
                                    self.pressed_button_rect = rect.copy()
                                    break
                        elif self.app_state == AppState.GAME:
                            for rect in (self.btn_symbol_o, self.btn_symbol_x, self.btn_restart, self.btn_exit_home):
                                if rect.collidepoint(mx, my):
                                    self.pressed_button_rect = rect.copy()
                                    break
                            if self.pressed_button_rect.width == 1:
                                action_items, _, _ = self._action_buttons_view()
                                for rect, _, _ in action_items:
                                    if rect.collidepoint(mx, my):
                                        self.pressed_button_rect = rect.copy()
                                        break
                        continue

                    if self.show_rules:
                        self._handle_rules_click(mx, my)
                    else:
                        if self.app_state == AppState.GAME and self.feedback_thumb_rect.collidepoint(mx, my):
                            self.feedback_dragging = True
                            self.feedback_drag_offset = my - self.feedback_thumb_rect.y

                        if self.app_state == AppState.HOME:
                            self._handle_home_click(mx, my)
                        elif self.app_state == AppState.MODE_MENU:
                            self._handle_mode_menu_click(mx, my)
                        elif self.app_state == AppState.OPTION_MENU:
                            self._handle_option_menu_click(mx, my)
                        elif self.app_state == AppState.REVEAL:
                            self._handle_reveal_click(mx, my)
                        elif self.app_state == AppState.GAME:
                            self._handle_game_click(mx, my)
                        elif self.app_state == AppState.CREDITS:
                            self._handle_credits_click(mx, my)

                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    mx, my = event.pos
                    if self.pressed_button_rect is not None and self.pressed_button_rect.collidepoint(mx, my):
                        self._on_text_button_release(mx, my)

                    self.left_mouse_down = False
                    self.slider_drag = False
                    self.feedback_dragging = False
                    self.action_dragging = False
                    self.pressed_button_rect = None
                    if self.app_state == AppState.REVEAL:
                        self.reveal_hold_pid = None
                        self.reveal_hint_alpha = 0.0

                if event.type == pygame.MOUSEMOTION:
                    if self.slider_drag and self.app_state == AppState.OPTION_MENU:
                        self._update_slider(event.pos[0])
                        self._play_sfx("tick", throttle_ms=35)

                    if self.action_dragging and self.app_state == AppState.GAME:
                        view = self._action_viewport_rect()
                        raw = self._action_buttons()
                        if raw:
                            min_y = min(r.y for r, _, _ in raw)
                            max_bottom = max(r.bottom for r, _, _ in raw)
                            max_scroll = max(0, (max_bottom - min_y) - view.height)
                            if max_scroll > 0:
                                track_h = view.height
                                thumb_h = max(24, int(track_h * (view.height / (view.height + max_scroll))))
                                move_range = track_h - thumb_h
                                target_top = event.pos[1] - self.action_drag_offset
                                clamped_top = max(view.y, min(view.y + move_range, target_top))
                                ratio = (clamped_top - view.y) / move_range if move_range > 0 else 0.0
                                self.action_scroll_target = ratio * max_scroll
                                self._play_sfx("tick", throttle_ms=35)

                    if self.feedback_dragging and self.app_state == AppState.GAME:
                        u = self._u
                        content_y = self.feedback_rect.y + u(40)
                        content_h = self.feedback_rect.height - u(44)
                        line_h = max(self.font_rule.get_height() + u(4), u(20))
                        visible = max(1, content_h // line_h)
                        content_x = self.feedback_rect.x + u(10)
                        track_x = self.feedback_rect.right - u(14)
                        max_sep_w = track_x - content_x - u(6)
                        rows = self._feedback_rows(max_sep_w)
                        max_scroll = max(0, len(rows) - visible)

                        if len(rows) > visible:
                            thumb_h = max(u(24), int(content_h * (visible / len(rows))))
                            move_range = content_h - thumb_h
                            target_top = event.pos[1] - self.feedback_drag_offset
                            clamped_top = max(content_y, min(content_y + move_range, target_top))
                            ratio = (clamped_top - content_y) / move_range if move_range > 0 else 0.0
                            self.feedback_scroll_target = float(int(round(ratio * max_scroll)))
                            self._play_sfx("tick", throttle_ms=35)

                if event.type == pygame.MOUSEWHEEL:
                    mx, my = pygame.mouse.get_pos()
                    u = self._u

                    if self.app_state == AppState.OPTION_MENU:
                        slider_area = pygame.Rect(self.slider_rect.x - u(12), self.slider_rect.y - u(26), self.slider_rect.width + u(140), u(40))
                        if slider_area.collidepoint(mx, my):
                            self.turn_time_limit = max(TIME_MIN, min(TIME_MAX, self.turn_time_limit + event.y))
                            self._play_sfx("tick", throttle_ms=35)
                            continue

                    if self.app_state == AppState.GAME and self.feedback_rect.collidepoint((mx, my)):
                        self.feedback_scroll_target -= event.y * 3
                        self._play_sfx("tick", throttle_ms=35)

                    if self.app_state == AppState.GAME:
                        view = self._action_viewport_rect()
                        raw = self._action_buttons()
                        if view.collidepoint((mx, my)) and raw:
                            min_y = min(r.y for r, _, _ in raw)
                            max_bottom = max(r.bottom for r, _, _ in raw)
                            max_scroll = max(0, (max_bottom - min_y) - view.height)
                            if max_scroll > 0:
                                self.action_scroll_target = max(0.0, min(float(max_scroll), self.action_scroll_target - event.y * 24.0))
                                self._play_sfx("tick", throttle_ms=35)

            if self.app_state != self._last_app_state:
                self.ui_transition_alpha = 170.0
                self._last_app_state = self.app_state

            if self.ui_transition_alpha > 0:
                self.ui_transition_alpha = max(0.0, self.ui_transition_alpha - dt * 420.0)

            counting_in_game = self.app_state == AppState.GAME or (self.app_state == AppState.CREDITS and self.credits_return_state == AppState.GAME)
            if counting_in_game and not self.game_over:
                if not self.open_waiting_consent:
                    self.turn_time_left -= dt
                    if self.turn_time_left <= 0:
                        self.turn_time_left = 0
                        self._on_timeout()

            self._update_hover_open_line()
            target_idx = self.hover_open_line_idx
            if target_idx is not None:
                if self.hover_open_line_draw_idx != target_idx:
                    self.hover_open_line_draw_idx = target_idx
                    self.hover_open_line_alpha = 0.0
                self.hover_open_line_alpha += (1.0 - self.hover_open_line_alpha) * min(1.0, dt * 14.0)
            else:
                self.hover_open_line_alpha += (0.0 - self.hover_open_line_alpha) * min(1.0, dt * 14.0)
                if self.hover_open_line_alpha <= 0.01:
                    self.hover_open_line_alpha = 0.0
                    self.hover_open_line_draw_idx = None

            if self.rejected_line_cells is not None:
                self.rejected_line_alpha += (0.0 - self.rejected_line_alpha) * min(1.0, dt * 8.0)
                if self.rejected_line_alpha <= 0.01:
                    self.rejected_line_alpha = 0.0
                    self.rejected_line_cells = None

            self.screen.fill(BG_COLOR)
            self._draw_board()

            if self.app_state == AppState.HOME:
                self._draw_home()
            elif self.app_state == AppState.MODE_MENU:
                self._draw_mode_menu()
            elif self.app_state == AppState.OPTION_MENU:
                self._draw_option_menu()
            elif self.app_state == AppState.REVEAL:
                self._draw_reveal()
            elif self.app_state == AppState.GAME:
                self._draw_game_panel()
            elif self.app_state == AppState.CREDITS:
                self._draw_credits()

            credits_text = self._t("返回", "Back") if self.app_state == AppState.CREDITS else "Credits"
            self._draw_text_button(self.btn_home_credits, credits_text, active=(self.app_state == AppState.CREDITS))

            if self.show_rules or self.rules_overlay_alpha > 0.01:
                self._draw_rules_overlay()

            if self.ui_transition_alpha > 0:
                panel_fade_x = max(self.panel_x - 8, 0)
                panel_fade_w = WINDOW_WIDTH - panel_fade_x
                fade = pygame.Surface((panel_fade_w, WINDOW_HEIGHT), pygame.SRCALPHA)
                fade.fill((12, 16, 26, int(self.ui_transition_alpha)))
                self.screen.blit(fade, (panel_fade_x, 0))

            pygame.display.flip()


if __name__ == "__main__":
    Gotcha().run()
