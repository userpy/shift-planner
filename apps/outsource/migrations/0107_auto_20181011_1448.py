# Generated by Django 2.0.5 on 2018-10-11 11:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('outsource', '0106_auto_20181010_1703'),
    ]

    operations = [
        migrations.AlterField(
            model_name='storearea',
            name='color',
            field=models.CharField(blank=True, choices=[('Основные', [('#66ade7', '#66ade7'), ('#a8b8d2', '#a8b8d2'), ('#9cd27c', '#9cd27c'), ('#47d9d4', '#47d9d4'), ('#d97abb', '#d97abb')]), ('Красные', [('indianred', 'IndianRed'), ('lightcoral', 'LightCoral'), ('salmon', 'Salmon'), ('darksalmon', 'DarkSalmon'), ('lightsalmon', 'LightSalmon'), ('crimson', 'Crimson'), ('red', 'Red'), ('firebrick', 'FireBrick'), ('darkred', 'DarkRed')]), ('Розовые', [('pink', 'Pink'), ('lightpink', 'LightPink'), ('hotpink', 'HotPink'), ('deeppink', 'DeepPink'), ('mediumvioletred', 'MediumVioletRed'), ('palevioletred', 'PaleVioletRed')]), ('Оранжевые', [('coral', 'Coral'), ('tomato', 'Tomato'), ('orangered', 'OrangeRed'), ('darkorange', 'DarkOrange'), ('orange', 'Orange')]), ('Жёлтые', [('gold', 'Gold'), ('yellow', 'Yellow'), ('lightyellow', 'LightYellow'), ('lemonchiffon', 'LemonChiffon'), ('lightgoldenrodyellow', 'LightGoldenrodYellow'), ('papayawhip', 'PapayaWhip'), ('moccasin', 'Moccasin'), ('peachpuff', 'PeachPuff'), ('palegoldenrod', 'PaleGoldenrod'), ('khaki', 'Khaki'), ('darkkhaki', 'DarkKhaki')]), ('Фиолетовые', [('lavender', 'Lavender'), ('thistle', 'Thistle'), ('plum', 'Plum'), ('violet', 'Violet'), ('orchid', 'Orchid'), ('fuchsia', 'Fuchsia'), ('mediumorchid', 'MediumOrchid'), ('mediumpurple', 'MediumPurple'), ('blueviolet', 'BlueViolet'), ('darkviolet', 'DarkViolet'), ('darkorchid', 'DarkOrchid'), ('darkmagenta', 'DarkMagenta'), ('purple', 'Purple'), ('indigo', 'Indigo'), ('slateblue', 'SlateBlue'), ('darkslateblue', 'DarkSlateBlue')]), ('Зелёные', [('greenyellow', 'GreenYellow'), ('chartreuse', 'Chartreuse'), ('lawngreen', 'LawnGreen'), ('lime', 'Lime'), ('limegreen', 'LimeGreen'), ('palegreen', 'PaleGreen'), ('lightgreen', 'LightGreen'), ('mediumspringgreen', 'MediumSpringGreen'), ('springgreen', 'SpringGreen'), ('mediumseagreen', 'MediumSeaGreen'), ('seagreen', 'SeaGreen'), ('forestgreen', 'ForestGreen'), ('green', 'Green'), ('darkgreen', 'DarkGreen'), ('yellowgreen', 'YellowGreen'), ('olivedrab', 'OliveDrab'), ('olive', 'Olive'), ('darkolivegreen', 'DarkOliveGreen'), ('mediumaquamarine', 'MediumAquamarine'), ('darkseagreen', 'DarkSeaGreen'), ('lightseagreen', 'LightSeaGreen'), ('darkcyan', 'DarkCyan'), ('teal', 'Teal')]), ('Синие', [('aqua', 'Aqua'), ('lightcyan', 'LightCyan'), ('paleturquoise', 'PaleTurquoise'), ('aquamarine', 'Aquamarine'), ('turquoise', 'Turquoise'), ('mediumturquoise', 'MediumTurquoise'), ('darkturquoise', 'DarkTurquoise'), ('cadetblue', 'CadetBlue'), ('steelblue', 'SteelBlue'), ('lightsteelblue', 'LightSteelBlue'), ('powderblue', 'PowderBlue'), ('lightblue', 'LightBlue'), ('skyblue', 'SkyBlue'), ('lightskyblue', 'LightSkyBlue'), ('deepskyblue', 'DeepSkyBlue'), ('dodgerblue', 'DodgerBlue'), ('cornflowerblue', 'CornflowerBlue'), ('mediumslateblue', 'MediumSlateBlue'), ('royalblue', 'RoyalBlue'), ('blue', 'Blue'), ('mediumblue', 'MediumBlue'), ('darkblue', 'DarkBlue'), ('navy', 'Navy'), ('midnightblue', 'MidnightBlue')]), ('Коричневые', [('cornsilk', 'Cornsilk'), ('blanchedalmond', 'BlanchedAlmond'), ('bisque', 'Bisque'), ('navajowhite', 'NavajoWhite'), ('wheat', 'Wheat'), ('burlywood', 'BurlyWood'), ('tan', 'Tan'), ('rosybrown', 'RosyBrown'), ('sandybrown', 'SandyBrown'), ('goldenrod', 'Goldenrod'), ('darkgoldenrod', 'DarkGoldenrod'), ('peru', 'Peru'), ('chocolate', 'Chocolate'), ('saddlebrown', 'SaddleBrown'), ('sienna', 'Sienna'), ('brown', 'Brown'), ('maroon', 'Maroon')]), ('Белые', [('white', 'White'), ('snow', 'Snow'), ('honeydew', 'Honeydew'), ('mintcream', 'MintCream'), ('azure', 'Azure'), ('aliceblue', 'AliceBlue'), ('ghostwhite', 'GhostWhite'), ('whitesmoke', 'WhiteSmoke'), ('seashell', 'Seashell'), ('beige', 'Beige'), ('oldlace', 'OldLace'), ('floralwhite', 'FloralWhite'), ('ivory', 'Ivory'), ('antiquewhite', 'AntiqueWhite'), ('linen', 'Linen'), ('lavenderblush', 'LavenderBlush'), ('mistyrose', 'MistyRose')]), ('Серые', [('gainsboro', 'Gainsboro'), ('lightgray', 'LightGray'), ('silver', 'Silver'), ('darkgray', 'DarkGray'), ('gray', 'Gray'), ('dimgray', 'DimGray'), ('lightslategray', 'LightSlateGray'), ('slategray', 'SlateGray'), ('darkslategray', 'DarkSlateGray'), ('black', 'Black')])], max_length=120, null=True, verbose_name='Цвет'),
        ),
        migrations.AlterField(
            model_name='storearea',
            name='icon',
            field=models.CharField(blank=True, max_length=120, null=True, verbose_name='Иконка'),
        ),
    ]
