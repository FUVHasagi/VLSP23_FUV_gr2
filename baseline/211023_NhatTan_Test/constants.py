import emoji


NP_SEED = 14


ALL_EMOJI = list(emoji.EMOJI_DATA.keys())
ALL_EMOJI.append("♡")
ALL_EMOJI.append("★")
ALL_EMOJI.append("=)")  # TODO: HANDLE LONGER CASE =))))))
ALL_EMOJI.append(":)")  # TODO: HANDLE LONGER CASE :))))))
ALL_EMOJI.append("^ _ ^")
# ALL_EMOJI.append("^^")
ALL_EMOJI.append("⚘")
ALL_EMOJI.append("☆")
ALL_EMOJI.append("◆")
ALL_EMOJI.append("·")
ALL_EMOJI.append("•")
ALL_EMOJI.append("●")
ALL_EMOJI.append("⊡")
ALL_EMOJI.append("▼")
ALL_EMOJI.append("…")

FONT_ERRORS = ["�", ""]

ALL_NUM = '0123456789'

VI_ALL = 'AĂÂBCDĐEÊGHIKLMNOÔƠPQRSTUƯVXYÁÀẢÃẠẮẰẲẴẶẤẦẨẪẬÉÈẺẼẸẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌỐỒỔỖỘỚỜỞỠỢÚÙỦŨỤỨỪỬỮỰÝỲỶỸỴaăâbcdđeêghiklmnoôơpqrstuưvxyáàảãạắằẳẵặấầẩẫậéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ'
EXTRA_LETTER = 'fjwzFJWZ'
VI_ALL = VI_ALL + EXTRA_LETTER + ALL_NUM


SPECIAL_SPACING = [' ', '​', '﻿']



