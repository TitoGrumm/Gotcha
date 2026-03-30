License : MIT License


Statement

	This game does not advocate or condone the practice of ' doxxing ' ( also known as ' box - opening ' in Chinese context ) ; on the contrary , we firmly oppose such behaviour . Any references to this within the game are intended solely for the purposes of adding humour and light - hearted banter , and carry no other connotations .

	Player feedback is welcome during the beta and RC versions and will be considered adopting and implementing . If you have suggestions for a better name or any other feedback , please contact ' tito_grumm@foxmail.com ' . Looking forward to hearing from you !


Environment Building

	· This game has been built , developed , tested and maintained exclusively on Windows 11 ; Its performance on other platforms is not guaranteed .

	· Before running ' Gotcha.py ' , please ensure your Windows meets the following requirements :

		- Install Python 3.10 + ( the ' Add Python to PATH ' box ticked )

		- Install pygame :

			-- Open the Windows Command Prompt : press Win + R , type ' cmd ' in the dialogue box that pops - up , then press Enter ; or right - click the Windows icon on the taskbar , locate ' Console ' or ' Terminal ' or ' Windows PowerShell ' and click it.

			-- Select one of the following commands , copy and paste it into the terminal , then press Enter . Note that the commands are split across two lines . If one of the options is unavailable , try the other .

				python -m pip install --upgrade pip
				python -m pip install pygame

				or

				py -m pip install --upgrade pip
				py -m pip install pygame

				or

				python -m pip install --upgrade pip
				python -m pip install pygame-ce

				or

				py -m pip install --upgrade pip
				py -m pip install pygame-ce

		- ( optional ) To verify that pygame has been successfully installed , enter the following in the terminal :

			python -c “import pygame; print(pygame.__version__)”

			or

			py -c “import pygame; print(pygame.__version__)”

			If the output is

			pygame-ce 2.5.7 (SDL 2.32.10, Python 3.14.3)
			2.5.7

			or

			pygame 2.6.1 (SDL 2.28.4, Python 3.9.13)
			2.6.1

			or similar version information , this indicates that pygame has been successfully installed .


Versions and Release Dates

	· v 0.1 ( beta )							2026 / 3 / 30


Release Notes

	· v 0.1

		Released the beta version . This version only implements local multiplayer functionality , so the first three custom options are purely decorative . Nevertheless , feel free to chat away !
