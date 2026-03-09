"""PersonService 单元测试。"""

import pytest
from datetime import datetime

from app.models.enums import Gender, Source
from app.schemas.person import PersonCreate, PersonUpdate
from app.services.person import PersonService


class TestPersonService:
    """PersonService 单元测试。"""

    @pytest.mark.asyncio
    async def test_create_person(self, db_session):
        """测试创建人员。"""
        service = PersonService()
        person_data = PersonCreate(
            name="张三",
            phone="13800138000",
            city="北京",
            gender=Gender.MALE,
            source=Source.BOSS,
        )
        created_by = 1

        person = await service.create(db_session, person_data, created_by)

        assert person.id is not None
        assert person.name == "张三"
        assert person.phone == "13800138000"
        assert person.city == "北京"
        assert person.gender == Gender.MALE
        assert person.source == Source.BOSS
        assert person.reusable is True
        assert person.created_by == created_by

    @pytest.mark.asyncio
    async def test_create_person_duplicate_phone(self, db_session):
        """测试手机号重复时抛出异常。"""
        service = PersonService()
        person_data = PersonCreate(
            name="张三",
            phone="13800138000",
            city="北京",
        )
        await service.create(db_session, person_data, created_by=1)

        # 再次创建相同手机号
        with pytest.raises(ValueError, match="手机号已存在"):
            await service.create(db_session, person_data, created_by=1)

    @pytest.mark.asyncio
    async def test_get_person_by_id(self, db_session):
        """测试根据 ID 获取人员。"""
        service = PersonService()
        person_data = PersonCreate(
            name="张三",
            phone="13800138000",
            city="北京",
        )
        created = await service.create(db_session, person_data, created_by=1)

        person = await service.get_by_id(db_session, created.id)

        assert person is not None
        assert person.id == created.id
        assert person.name == "张三"

    @pytest.mark.asyncio
    async def test_get_person_by_id_not_found(self, db_session):
        """测试获取不存在的人员返回 None。"""
        service = PersonService()

        person = await service.get_by_id(db_session, 999)

        assert person is None

    @pytest.mark.asyncio
    async def test_get_person_list(self, db_session):
        """测试获取人员列表。"""
        service = PersonService()

        # 创建多个人员
        for i in range(5):
            await service.create(
                db_session,
                PersonCreate(
                    name=f"用户{i}",
                    phone=f"1380013800{i}",
                    city="北京",
                ),
                created_by=1,
            )

        persons, total = await service.get_list(db_session, skip=0, limit=3)

        assert len(persons) == 3
        assert total == 5

    @pytest.mark.asyncio
    async def test_get_person_list_with_filter(self, db_session):
        """测试带筛选的人员列表。"""
        service = PersonService()

        # 创建不同城市的人员
        await service.create(
            db_session,
            PersonCreate(name="北京用户", phone="13800138001", city="北京"),
            created_by=1,
        )
        await service.create(
            db_session,
            PersonCreate(name="上海用户", phone="13800138002", city="上海"),
            created_by=1,
        )

        persons, total = await service.get_list(db_session, city="北京")

        assert len(persons) == 1
        assert persons[0].city == "北京"

    @pytest.mark.asyncio
    async def test_search_person_by_name(self, db_session):
        """测试按姓名搜索人员。"""
        service = PersonService()

        await service.create(
            db_session,
            PersonCreate(name="张三", phone="13800138001", city="北京"),
            created_by=1,
        )
        await service.create(
            db_session,
            PersonCreate(name="李四", phone="13800138002", city="北京"),
            created_by=1,
        )

        persons, total = await service.get_list(db_session, search="张")

        assert len(persons) == 1
        assert persons[0].name == "张三"

    @pytest.mark.asyncio
    async def test_search_person_by_phone(self, db_session):
        """测试按手机号搜索人员。"""
        service = PersonService()

        await service.create(
            db_session,
            PersonCreate(name="张三", phone="13800138001", city="北京"),
            created_by=1,
        )
        await service.create(
            db_session,
            PersonCreate(name="李四", phone="13800138002", city="北京"),
            created_by=1,
        )

        persons, total = await service.get_list(db_session, search="13800138001")

        assert len(persons) == 1
        assert persons[0].phone == "13800138001"

    @pytest.mark.asyncio
    async def test_update_person(self, db_session):
        """测试更新人员信息。"""
        service = PersonService()

        created = await service.create(
            db_session,
            PersonCreate(name="张三", phone="13800138000", city="北京"),
            created_by=1,
        )

        update_data = PersonUpdate(name="张三三", city="上海")
        updated = await service.update(db_session, created.id, update_data)

        assert updated.name == "张三三"
        assert updated.city == "上海"
        assert updated.phone == "13800138000"  # 未修改的字段保持不变

    @pytest.mark.asyncio
    async def test_update_person_not_found(self, db_session):
        """测试更新不存在的人员返回 None。"""
        service = PersonService()

        updated = await service.update(
            db_session, 999, PersonUpdate(name="新名字")
        )

        assert updated is None

    @pytest.mark.asyncio
    async def test_delete_person(self, db_session):
        """测试删除人员。"""
        service = PersonService()

        created = await service.create(
            db_session,
            PersonCreate(name="张三", phone="13800138000", city="北京"),
            created_by=1,
        )

        result = await service.delete(db_session, created.id)

        assert result is True

        # 验证已删除
        person = await service.get_by_id(db_session, created.id)
        assert person is None

    @pytest.mark.asyncio
    async def test_delete_person_not_found(self, db_session):
        """测试删除不存在的人员返回 False。"""
        service = PersonService()

        result = await service.delete(db_session, 999)

        assert result is False

    @pytest.mark.asyncio
    async def test_get_person_with_projects(self, db_session):
        """测试获取人员及其项目状态。"""
        service = PersonService()

        # 创建人员
        person = await service.create(
            db_session,
            PersonCreate(name="张三", phone="13800138000", city="北京"),
            created_by=1,
        )

        # 获取带项目的人员详情
        person_with_projects = await service.get_with_projects(db_session, person.id)

        assert person_with_projects is not None
        assert person_with_projects.id == person.id
        assert hasattr(person_with_projects, "person_projects")

    @pytest.mark.asyncio
    async def test_update_person_duplicate_phone(self, db_session):
        """测试更新手机号时与其他人员冲突。"""
        service = PersonService()

        # 创建两个人员
        person1 = await service.create(
            db_session,
            PersonCreate(name="张三", phone="13800138001", city="北京"),
            created_by=1,
        )
        await service.create(
            db_session,
            PersonCreate(name="李四", phone="13800138002", city="北京"),
            created_by=1,
        )

        # 尝试将 person1 的手机号改为已存在的手机号
        with pytest.raises(ValueError, match="手机号已存在"):
            await service.update(db_session, person1.id, PersonUpdate(phone="13800138002"))

    @pytest.mark.asyncio
    async def test_get_person_list_empty(self, db_session):
        """测试空数据库返回空列表。"""
        service = PersonService()
        persons, total = await service.get_list(db_session)

        assert persons == []
        assert total == 0

    @pytest.mark.asyncio
    async def test_search_with_special_characters(self, db_session):
        """测试搜索包含特殊字符时被正确转义。"""
        service = PersonService()

        # 创建包含 % 和 _ 的名字
        await service.create(
            db_session,
            PersonCreate(name="测试%用户", phone="13800138001", city="北京"),
            created_by=1,
        )
        await service.create(
            db_session,
            PersonCreate(name="测试_用户", phone="13800138002", city="北京"),
            created_by=1,
        )
        await service.create(
            db_session,
            PersonCreate(name="普通用户", phone="13800138003", city="北京"),
            created_by=1,
        )

        # 搜索 % 会被转义，不会匹配所有记录（如果不转义，% 会匹配所有）
        # 由于转义后搜索的是字面的 % 字符，应该只匹配"测试%用户"
        persons, total = await service.get_list(db_session, search="%")
        assert total == 1
        assert persons[0].name == "测试%用户"

        # 搜索 _ 会被转义，只匹配"测试_用户"
        persons, total = await service.get_list(db_session, search="_")
        assert total == 1
        assert persons[0].name == "测试_用户"

        # 搜索普通文本应该匹配包含该文本的记录
        persons, total = await service.get_list(db_session, search="测试")
        assert total == 2
