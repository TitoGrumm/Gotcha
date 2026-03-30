License : MIT License
开源许可证：MIT License


声明

	本游戏并没有提倡“开盒”这一行为；相反，作者及所有制作人员都坚决抵制这种行为。在游戏中仅作增添趣味性和调侃之用，没有赋予其他含义。

	本游戏在 beta 和 RC 阶段接受玩家反馈，并会考虑采纳修改。如您有更好的名字建议或其他任何反馈，请联系 tito_grumm@foxmail.com。期待听到您的声音！


环境配置

	· 本游戏仅在 Windows 11 上搭建、开发、测试和维护，对于在其他平台上的可运行性不做保证。

	· 在运行 Gotcha.py 之前，请先确保您的 Windows 已完成以下配置：

		- 安装 Python 3.10 +（勾选“Add Python to PATH”）

		- 安装 pygame：

			-- 运行 Windows 终端：按 Win + R，在弹出的对话框中输入 cmd，再按回车；或右键点击任务栏的 Win 图标，找到“终端”并左键点击。

			-- 将以下代码选择其一复制并粘贴到终端中，再按回车。注意代码有两行。若其中某一项不可用，可尝试使用其他选项。

				python -m pip install --upgrade pip
				python -m pip install pygame

				或

				py -m pip install --upgrade pip
  				py -m pip install pygame

				或

				python -m pip install --upgrade pip
				python -m pip install pygame-ce

				或

				py -m pip install --upgrade pip
				py -m pip install pygame-ce

		-（可选）为验证是否已成功安装 pygame，可以在终端中输入：

			python -c "import pygame; print(pygame.__version__)"

			或

			py -c "import pygame; print(pygame.__version__)"

			若返回

			pygame-ce 2.5.7 (SDL 2.32.10, Python 3.14.3)
			2.5.7

			或

			pygame 2.6.1 (SDL 2.28.4, Python 3.9.13)
			2.6.1

			之类的版本号信息，说明已成功安装 pygame。


版本及发布日期

	· v 0.1 ( beta )							2026 / 3 / 30


更新日志

	· v 0.1

		发布了 beta 版本。此版本仅实现了本地多人游玩的功能，因此前三个自定义选项只起到了一个造型上的作用。尽管嘴炮吧！
