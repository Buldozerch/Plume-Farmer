from .models import User
import random
import json
from datetime import datetime
from sqlalchemy import select, update, text
from libs.eth_async.utils.utils import parse_proxy


class DB:
    def __init__(self, session):
        self.session = session

    async def add_wallet(
        self,
        private_key: str,
        public_key: str,
        user_agent: str,
        proxy: str | None = None,
    ):
        """Добавляет кошелек в базу данных"""
        wallet = User(
            private_key=private_key,
            public_key=public_key,
            proxy=proxy,
            user_agent=user_agent,
            proxy_status="OK",
        )
        try:
            self.session.add(wallet)
            await self.session.flush()  # Проверяем наличие ошибок при добавлении
        except Exception as e:
            return False
        return True

    async def update_proxy(self, user_id: int, available_proxies: list):
        """Обновляет прокси для пользователя"""
        existing_proxies = await self.session.execute(select(User.proxy))
        existing_proxies = {
            proxy[0] for proxy in existing_proxies.all()
        }  # Преобразуем в множество

        # Фильтруем список, оставляя только уникальные прокси
        unique_proxies = list(set(available_proxies) - existing_proxies)
        if not unique_proxies:
            raise ValueError("Нет доступных уникальных прокси!")

        # Выбираем случайный уникальный прокси
        new_proxy = random.choice(unique_proxies)
        new_proxy = parse_proxy(new_proxy)

        # Обновляем прокси для пользователя
        user = await self.session.get(User, user_id)
        if user:
            user.proxy = new_proxy
            user.proxy_status = "OK"  # Сбрасываем статус при обновлении
            await self.session.commit()
            return new_proxy
        else:
            raise ValueError(f"Пользователь с id {user_id} не найден")

    async def get_all_wallets(self) -> list:
        """Получает все кошельки из базы данных"""
        result = await self.session.execute(
            select(User)
        )  # выполняем запрос ко всем записям в таблице
        wallets = result.scalars().all()  # возвращаем все строки из таблицы как список
        return wallets

    async def get_user(self, user_id: int):
        user = await self.session.get(User, user_id)
        return user

    async def mark_proxy_as_bad(self, user_id: int) -> bool:
        """
        Отмечает прокси пользователя как плохое

        Args:
            user_id: ID пользователя

        Returns:
            Статус успеха
        """
        try:
            user = await self.session.get(User, user_id)
            if not user:
                return False

            user.proxy_status = "BAD"
            await self.session.commit()
            return True
        except Exception as e:
            return False

    async def get_wallets_with_bad_proxy(self) -> list:
        """
        Получает список кошельков с плохими прокси

        Returns:
            Список кошельков
        """
        query = select(User).where(User.proxy_status == "BAD")
        result = await self.session.execute(query)
        return result.scalars().all()

    async def replace_bad_proxy(self, user_id: int, new_proxy: str) -> bool:
        """
        Заменяет плохое прокси пользователя

        Args:
            user_id: ID пользователя
            new_proxy: Новое прокси

        Returns:
            Статус успеха
        """
        try:
            user = await self.session.get(User, user_id)
            if not user:
                return False

            user.proxy = parse_proxy(new_proxy)
            user.proxy_status = "OK"
            await self.session.commit()
            return True
        except Exception as e:
            return False
