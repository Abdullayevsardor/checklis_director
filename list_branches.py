import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings

async def main():
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.begin() as conn:
        result = await conn.execute(text('SELECT id, name FROM branches ORDER BY id'))
        print('BRANCH_ID | NAME')
        for row in result:
            print(f'{row[0]} | {row[1]}')
    await engine.dispose()

if __name__ == '__main__':
    asyncio.run(main())









# Foydalanish uchun branch_idlar
# 5 — ОТДЕЛ КАЛЬКУЛЯЦИИ
# 6 — MW21-GOLDENLIFE
# 7 — MW12-MAGIC CITY
# 8 — MW15-AVIASOZLAR
# 9 — МОРОЖЕНОЕ
# 10 — MW07-MINOR
# 11 — MW02-GORKIY
# 12 — MW03-GRAND MIR
# 13 — MW04-ROISON
# 14 — MW01-UNIVERSAM
# 15 — MW10-PARKENT
# 16 — MW05-SERGELI
# 17 — МАРКЕТИНГ
# 18 — ОТДЕЛ ТЕХНИЧЕСКОЙ ПОДДЕРЖКИ
# 19 — ОТДЕЛ КАДРОВОГО АДМИНИСТРИРОВАНИЯ
# 20 — MW22-ECO CHIMGAN
# 21 — MW16-YANGISHAHAR (MEGAPLANET)
# 22 — КОЛЛ-ЦЕНТР
# 23 — MW08-SAYRAM
# 24 — MW13-KATORTOL (PARUS)
# 25 — MW14-RISOVIY
# 26 — MW06-NEXT
# 27 — MW20-ALAYSKIY
# 28 — MW19-BERUNIY
# 29 — MW23-YANGIYO'L
# 30 — MW09-MUQIMIY
# 31 — MW18-ATLAS
# 32 — ОФИС
# 33 — MW17-DRUJBA
# 34 — БЛОК РАЗВИТИЯ СЕТИ
# 35 — ОТДЕЛ БЕЗОПАСНОСТИ И ВИДЕОНАБЛЮДЕНИЯ
# 36 — ОТДЕЛ ТЕХНИЧЕСКОГО ОБСЛУЖИВАНИЯ ПБО
# 37 — ОТДЕЛ ПОДБОРА ПЕРСОНАЛА
# 38 — ОТДЕЛ ТРУДА И ТЕХНИКИ БЕЗОПАСНОСТИ
# 39 — ОТДЕЛ БУХГАЛТЕРСКОГО УЧЁТА
# 40 — УПРАВЛЕНИЕ ПБО
# 41 — ОТДЕЛ ОБУЧЕНИЯ
# 42 — ЮРИДИЧЕСКИЙ ОТДЕЛ
# 43 — ФИНАНСОВЫЙ ОТДЕЛ
# 44 — ОТДЕЛ ЗАКУПОК И СНАБЖЕНИЯ
# 45 — АДМИНИСТРАТИВНО-ХОЗЯЙСТВЕННЫЙ ОТДЕЛ
# 46 — ОТДЕЛ ПОДДЕРЖКИ ПБО
# 47 — ОТДЕЛ СЭС
# 49 — Test filial
 