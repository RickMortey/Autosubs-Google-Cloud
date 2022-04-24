# autosubs
autosubs for video (python)

Автоматическое добавление субтитров в видео на основе Google Cloud Speech-to-text API

### Входные данные
Видео формата .mp4 длительностью меньше минуты.
Для корректного отображения они должны быть вертикальными.

### Спецификация входных данных

Для наилучшего результата видео должно быть с хорошим звуком. Без музыки, громких шумов на заднем фоне (например, не стоит записывать видео на шоссе).
Речь должна быть разборчива.
Скорость обработки видео напрямую зависит от длительности видео и сложности обрабатываемого материала с точки зрения звука. Поэтому, чем меньше видео,
тем быстрее оно обработается. 
В данной конфигурации используется recognize, который может обрабатывать видео длительностью до одной минуты

### Необходимые ресурсы

Разработка велась на Linux Ubuntu 20.04, поэтому программа должна гарантированно работать на ней.

Для корректной работы программы необходимо установить следующие программы: ffmpeg, sox, ImageMagick (можно установить с помощью pip install src/core/resources/requirements.txt) 

Также необходимо завести свой токен в Google Cloud Platform и назвать его ml-dev.json, поместив его в папку src/core/resources

Вот последовательные шаги, которые нужно сделать:

0. Зайти на сайт Google Cloud Platform, зарегистрироваться, воспользоваться бесплатным тестовым периодом или ничего не делать (по логике, до 60 минут использования Cloud Speech-to-Text API бесплатны). Если вдруг при запуске ничего не сработает, достаточно закинуть сумму в размере 10 рублей, но можно и больше.
1. Перейти на вкладку IAM & Admin, создать сервисный аккаунт: назвать его и дать описание (опционально)
2. На следующем шаге необходимо присвоить роль ML Engine Developer
3. Дальше появится возможность создать json-ключ. Создайте его, назовите ml-dev.json, сохраните его на компьютер и поместите в папку src/core/resources
4. Пройти в API Library, найти Cloud Speech-to-Text API и нажать на кнопку "Enable Billing"
5. Вернуться во вкладку IAM & Admin, добавить роль сервисному аккаунту: ввести его адрес, добавить роль Project->Viewer. Сохранить

### Описание алгоритма:
Необходимо подать параметры с помощью аргументов при запуске скрипта из командной строки: --video - расположение видео. --language_code - язык, на котором разговаривают в видео и который надо распознать (корректно будет распознаваться только он). Стандартное значение - "ru". --max_chars - максимальное количество букв в одной строке. Стандартное значение - 8
1. далее из входного видео получается аудиодорожка формата .wav с определенным кодированием (для лучшей обработки)
2. Аудиодорожка обрабатывается нейронной сетью на серверах гугла, после чего на google storage появляется текст в виде .srt 
(с временными отметками начала/конца произнесения предложения, что очень важно для субтитров!). После чего файл скачивается на компьютер для локальной обработки
3. Субтитры накладываются на оригинальное видео с помощью MoviePy
4. Финальное видео с субтитрами называется *оригинальное_название_видео*_with_subs.mp4
5. ???
6. Profit!

### Тестирование:
Для тестирования подойдёт любое видео формата .mp4, удовлетворяющее требованиям спецификации
