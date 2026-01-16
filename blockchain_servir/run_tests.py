import unittest
import json
from app import create_app, db
from app.models import User, ActionDefinition, Block
from app.services.blockchain import BlockchainService

class TestServirSystem(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' # In-memory DB for tests
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            
            # Setup Admin User
            admin = User(name="Admin", email="admin@test.com", phone="000000000", role="admin")
            admin.set_password("admin123")
            db.session.add(admin)
            
            # Setup Regular User
            user = User(name="Jovem Teste", email="jovem@test.com", phone="5511999999999")
            user.set_password("123456")
            db.session.add(user)
            
            # Setup Action
            action = ActionDefinition(name="Leitura Bíblica", points=50, created_by_id=1)
            db.session.add(action)
            
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_blockchain_integrity(self):
        """Test if blocks are linked correctly"""
        with self.app.app_context():
            # Add Block 1
            BlockchainService.add_block(2, 1, {"action": "Test 1", "points": 50})
            # Add Block 2
            BlockchainService.add_block(2, 1, {"action": "Test 2", "points": 50})
            
            valid, msg = BlockchainService.validate_chain()
            self.assertTrue(valid, f"Blockchain invalid: {msg}")
            
            # Verify Points Update
            user = User.query.get(2)
            self.assertEqual(user.points, 100)
            self.assertEqual(user.stage, "Caminho") # 0-100 is Caminho
            
            # Add Block 3 (Level Up)
            BlockchainService.add_block(2, 1, {"action": "Test 3", "points": 10}) 
            # Total 110 -> Should be Formação
            
            user = User.query.get(2)
            self.assertEqual(user.points, 110)
            self.assertEqual(user.stage, "Formação")

    def test_webhook_flow(self):
        """Test the WhatsApp integration flow"""
        # 1. User not registered
        payload = {
            "data": {
                "key": {"remoteJid": "5511888888888@s.whatsapp.net"},
                "message": {"conversation": "/perfil"}
            }
        }
        res = self.client.post('/webhook', json=payload)
        self.assertIn("Você ainda não tem cadastro", res.json['reply'])
        
        # 2. User Registered - Check Profile
        payload['data']['key']['remoteJid'] = "5511999999999@s.whatsapp.net"
        res = self.client.post('/webhook', json=payload)
        self.assertIn("Jovem Teste", res.json['reply'])
        
        # 3. Perform Action
        payload['data']['message']['conversation'] = "/fazer 1"
        res = self.client.post('/webhook', json=payload)
        self.assertIn("registrada no Blockchain", res.json['reply'])

if __name__ == '__main__':
    unittest.main()
