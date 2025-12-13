from django.test import TestCase

# Create your tests here.
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from core.models import Admin
from django.contrib.auth.hashers import check_password, make_password


class AdminAuthAPITestCase(APITestCase):
    """
    测试管理员注册、登录、注销接口 (AdminAuthView)
    """

    def setUp(self):
        # 预先定义好路由名称
        self.register_url = reverse('admin-auth', kwargs={'action': 'register'})
        self.login_url = reverse('admin-auth', kwargs={'action': 'login'})
        self.logout_url = reverse('admin-auth', kwargs={'action': 'logout'})
        self.profile_url = reverse('admin-profile')  # 档案管理路由

        # 注册一个测试管理员供后续登录测试使用
        self.account = "testuser"
        self.password = "password123"
        self.admin = Admin.objects.create(
            account=self.account,
            password=make_password(self.password),  # 注意: 这里是明文，在测试中我们会手动进行哈希检查
            name="Original Name"
        )
        # # 注意: 真实的 AdminService.register_admin 会自动哈希密码，但这里我们绕过 Service 直接创建，
        # # 所以必须手动设置哈希后的密码才能通过 login 测试。
        # self.admin.password = check_password(self.password, 'fake_hash')  # 任意哈希值
        # self.admin.save()

    # ------------------ 注册 (Register) 测试 ------------------

    def test_register_success(self):
        """测试成功注册新管理员"""
        data = {"account": "newadmin", "password": "newpassword456", "name": "New Admin"}
        response = self.client.post(self.register_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Admin.objects.count(), 2)
        self.assertEqual(response.data['account'], 'newadmin')

        # 验证密码是否被哈希存储
        new_admin = Admin.objects.get(account='newadmin')
        self.assertTrue(check_password("newpassword456", new_admin.password))

    def test_register_duplicate_account(self):
        """测试注册时账号重复"""
        data = {"account": self.account, "password": "somepassword", "name": "Duplicate User"}
        response = self.client.post(self.register_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('account already exists', response.data['error'].lower())
        self.assertEqual(Admin.objects.count(), 1)  # 确认没有创建新用户

    # ------------------ 登录 (Login) 测试 ------------------

    def test_login_success(self):
        """测试成功登录"""
        data = {"account": self.account, "password": self.password}
        response = self.client.post(self.login_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['account'], self.account)
        # 验证 Session 是否被正确设置 (检查响应中的 session key)
        self.assertIn('sessionid', response.cookies)
        self.assertTrue(self.client.session.get('admin_id'))

    def test_login_failure_wrong_password(self):
        """测试密码错误导致登录失败"""
        data = {"account": self.account, "password": "wrongpassword"}
        response = self.client.post(self.login_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('Invalid account or password', response.data['error'])

    def test_login_failure_non_existent_account(self):
        """测试账号不存在导致登录失败"""
        data = {"account": "nonexistent", "password": "anypassword"}
        response = self.client.post(self.login_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('Invalid account or password', response.data['error'])

    # ------------------ 注销 (Logout) 测试 ------------------

    def test_logout_success(self):
        """测试成功注销"""
        # 先登录以设置 Session
        self.client.post(self.login_url, {"account": self.account, "password": self.password}, format='json')

        # 执行注销
        response = self.client.post(self.logout_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 验证 Session 是否被清除
        self.assertIsNone(self.client.session.get('admin_id'))


class AdminProfileAPITestCase(APITestCase):
    """
    测试管理员档案管理接口 (AdminProfileView)
    """

    def setUp(self):
        self.login_url = reverse('admin-auth', kwargs={'action': 'login'})
        self.profile_url = reverse('admin-profile')

        self.account = "profileuser"
        self.password = "profilepass"

        # 手动创建 Admin 实例,确保密码哈希
        hashed_password = make_password(self.password)
        self.admin = Admin.objects.create(
            account=self.account,
            password=hashed_password,
            name="Profile Target"
        )

        # 登录并获取 Session Cookie
        self.client.post(self.login_url, {"account": self.account, "password": self.password}, format='json')
        # self.admin = Admin.objects.get(account=self.account)  # 获取实例

    # ------------------ 权限 (Authorization) 测试 ------------------

    def test_profile_requires_authentication(self):
        """测试未登录用户无法访问 Profile 接口"""
        self.client.logout()  # 清除 Session
        response_get = self.client.get(self.profile_url, format='json')
        response_put = self.client.put(self.profile_url, {"name": "fail"}, format='json')

        self.assertEqual(response_get.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response_put.status_code, status.HTTP_401_UNAUTHORIZED)

    # ------------------ 获取信息 (GET) 测试 ------------------

    def test_get_profile_success(self):
        """测试成功获取个人信息"""
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['account'], self.account)
        self.assertEqual(response.data['name'], "Profile Target")
        self.assertNotIn('password', response.data)  # 确保密码没有被泄露

    # ------------------ 修改信息 (PUT/PATCH) 测试 ------------------

    def test_update_name_success(self):
        """测试成功修改姓名"""
        new_name = "Updated User Name"
        response = self.client.put(self.profile_url, {"name": new_name}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], new_name)

        # 验证数据库中的值已更新
        self.admin.refresh_from_db()
        self.assertEqual(self.admin.name, new_name)

    def test_update_password_success(self):
        """测试成功修改密码"""
        new_password = "verysecurepassword"
        response = self.client.put(self.profile_url, {"new_password": new_password}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['account'], self.account)

        # 验证新的密码能否用于登录
        self.admin.refresh_from_db()
        self.assertTrue(check_password(new_password, self.admin.password))

        # 验证旧密码失效
        self.assertFalse(check_password(self.password, self.admin.password))

    def test_update_both_success(self):
        """测试同时修改姓名和密码"""
        new_name = "Final Name"
        new_password = "FinalPassword"

        response = self.client.put(self.profile_url,
                                   {"name": new_name, "new_password": new_password},
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], new_name)

        # 验证数据库
        self.admin.refresh_from_db()
        self.assertEqual(self.admin.name, new_name)
        self.assertTrue(check_password(new_password, self.admin.password))