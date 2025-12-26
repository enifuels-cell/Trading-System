"""
Test for null safety in analyze_chart endpoint
Tests that the endpoint properly handles cases where trade_setup might be None or missing
"""

import json
import sys
from unittest.mock import patch, MagicMock
from app import app, db, User
import io

def test_analyze_with_none_trade_setup():
    """Test that analyze endpoint handles None trade_setup gracefully"""
    print("Testing analyze endpoint with None trade_setup...")
    
    with app.app_context():
        # Ensure database is initialized
        db.create_all()
        
        # Create a test user
        test_user = User.query.filter_by(username='testuser_null_safety').first()
        if not test_user:
            test_user = User(
                username='testuser_null_safety',
                email='test_null_safety@example.com',
                full_name='Test User'
            )
            test_user.set_password('testpass123')
            db.session.add(test_user)
            db.session.commit()
        
        with app.test_client() as client:
            # Login
            response = client.post('/api/login', json={
                'username': 'testuser_null_safety',
                'password': 'testpass123'
            })
            assert response.status_code == 200, "Login should succeed"
            
            # Mock the analyze_chart_with_ai function to return a response with None trade_setup
            with patch('app.analyze_chart_with_ai') as mock_analyze:
                mock_analyze.return_value = {
                    'success': True,
                    'analysis': {
                        'market_type': 'Crypto',
                        'patterns': ['triangle'],
                        'indicators': ['MA'],
                        'trade_setup': None,  # This is the key test case
                        'pattern_explanation': 'Test explanation',
                        'reasoning': 'Test reasoning',
                        'confidence_score': 75,
                        'risk_factors': ['volatility']
                    }
                }
                
                # Create a fake image file
                data = {
                    'chart': (io.BytesIO(b'fake image data'), 'test_chart.png'),
                    'trading_style': 'Day Trade',
                    'risk_profile': 'Balanced',
                    'asset_type': 'Crypto'
                }
                
                # Make request
                response = client.post('/api/analyze', 
                                     data=data,
                                     content_type='multipart/form-data')
                
                # Should succeed without NoneType error
                assert response.status_code == 200, f"Expected 200, got {response.status_code}"
                result = response.get_json()
                assert result['success'] == True, "Analysis should succeed"
    
    print("✓ Null trade_setup test passed")


def test_analyze_with_missing_trade_setup():
    """Test that analyze endpoint handles missing trade_setup gracefully"""
    print("\nTesting analyze endpoint with missing trade_setup...")
    
    with app.app_context():
        with app.test_client() as client:
            # Login
            response = client.post('/api/login', json={
                'username': 'testuser_null_safety',
                'password': 'testpass123'
            })
            assert response.status_code == 200, "Login should succeed"
            
            # Mock the analyze_chart_with_ai function to return a response without trade_setup
            with patch('app.analyze_chart_with_ai') as mock_analyze:
                mock_analyze.return_value = {
                    'success': True,
                    'analysis': {
                        'market_type': 'Forex',
                        'patterns': ['head and shoulders'],
                        'indicators': ['RSI'],
                        # trade_setup is completely missing
                        'pattern_explanation': 'Test explanation',
                        'reasoning': 'Test reasoning',
                        'confidence_score': 60,
                        'risk_factors': ['high volatility']
                    }
                }
                
                # Create a fake image file
                data = {
                    'chart': (io.BytesIO(b'fake image data'), 'test_chart.jpg'),
                    'trading_style': 'Swing',
                    'risk_profile': 'Conservative',
                    'asset_type': 'Forex'
                }
                
                # Make request
                response = client.post('/api/analyze', 
                                     data=data,
                                     content_type='multipart/form-data')
                
                # Should succeed without NoneType error
                assert response.status_code == 200, f"Expected 200, got {response.status_code}"
                result = response.get_json()
                assert result['success'] == True, "Analysis should succeed"
    
    print("✓ Missing trade_setup test passed")


def test_analyze_with_partial_trade_setup():
    """Test that analyze endpoint handles partial trade_setup data"""
    print("\nTesting analyze endpoint with partial trade_setup...")
    
    with app.app_context():
        with app.test_client() as client:
            # Login
            response = client.post('/api/login', json={
                'username': 'testuser_null_safety',
                'password': 'testpass123'
            })
            assert response.status_code == 200, "Login should succeed"
            
            # Mock the analyze_chart_with_ai function to return partial trade_setup
            with patch('app.analyze_chart_with_ai') as mock_analyze:
                mock_analyze.return_value = {
                    'success': True,
                    'analysis': {
                        'market_type': 'Stocks',
                        'patterns': ['flag'],
                        'indicators': ['MACD'],
                        'trade_setup': {
                            'direction': 'Long',
                            # Missing entry, stop_loss, and take_profit
                        },
                        'pattern_explanation': 'Test explanation',
                        'reasoning': 'Test reasoning',
                        'confidence_score': 80,
                        'risk_factors': []
                    }
                }
                
                # Create a fake image file
                data = {
                    'chart': (io.BytesIO(b'fake image data'), 'test_chart.png'),
                    'trading_style': 'Scalping',
                    'risk_profile': 'Aggressive',
                    'asset_type': 'Stocks'
                }
                
                # Make request
                response = client.post('/api/analyze', 
                                     data=data,
                                     content_type='multipart/form-data')
                
                # Should succeed without errors
                assert response.status_code == 200, f"Expected 200, got {response.status_code}"
                result = response.get_json()
                assert result['success'] == True, "Analysis should succeed"
    
    print("✓ Partial trade_setup test passed")


def run_tests():
    """Run all null safety tests"""
    print("=" * 60)
    print("Running Null Safety Tests for /api/analyze")
    print("=" * 60)
    
    try:
        test_analyze_with_none_trade_setup()
        test_analyze_with_missing_trade_setup()
        test_analyze_with_partial_trade_setup()
        
        print("\n" + "=" * 60)
        print("✓ All null safety tests passed!")
        print("=" * 60)
        return True
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
