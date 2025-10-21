from app.api.user_data.schemas import UserProfile

user1 = {'79123456789':
         {'profile':
          UserProfile(age=25,
                      monthly_income=30000,
                      employment_type='full_time',
                      has_property=True),
          'history': []
          }
         }
