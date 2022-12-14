from django.contrib import admin
from .models import Course
from .models import MlbGame
from .models import MlbPlayer
from .models import MlbTeam
from .models import MlbLocation
from .models import MlbAtBat
from .models import MlbUpcomingGames
from .models import MlbPlayerSimulations
from .models import MlbBovadaPitchersPostSimData
from .models import MlbBovadaPitchersBetComparison

from .models import Game
from .models import Team
from .models import People
from .models import Venue



# Register your models here.

admin.site.register(Course)
admin.site.register(MlbGame)
admin.site.register(MlbPlayer)
admin.site.register(MlbTeam)
admin.site.register(MlbLocation)
admin.site.register(MlbAtBat)
admin.site.register(MlbUpcomingGames)
admin.site.register(MlbPlayerSimulations)
admin.site.register(MlbBovadaPitchersPostSimData)
admin.site.register(MlbBovadaPitchersBetComparison)

admin.site.register(Game)
admin.site.register(Team)
admin.site.register(People)
admin.site.register(Venue)

