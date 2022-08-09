# Generated by Django 4.0.5 on 2022-08-07 21:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mlb', '0015_mlbbovadaupcomingbatters_mlbbovadaupcomingpitchers_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mlbbovadaupcomingpitchers',
            old_name='earned_runs_line',
            new_name='walks_over_odds',
        ),
        migrations.RenameField(
            model_name='mlbbovadaupcomingpitchers',
            old_name='hits_allowed_line',
            new_name='walks_under_odds',
        ),
        migrations.RemoveField(
            model_name='mlbbovadaupcomingpitchers',
            name='pitching_out_line',
        ),
        migrations.RemoveField(
            model_name='mlbbovadaupcomingpitchers',
            name='player_bov_id',
        ),
        migrations.RemoveField(
            model_name='mlbbovadaupcomingpitchers',
            name='strikeout_line',
        ),
        migrations.AddField(
            model_name='mlbbovadaupcomingpitchers',
            name='earned_runs_over_line',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mlbbovadaupcomingpitchers',
            name='earned_runs_under_line',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mlbbovadaupcomingpitchers',
            name='hits_allowed_over_line',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mlbbovadaupcomingpitchers',
            name='hits_allowed_under_line',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mlbbovadaupcomingpitchers',
            name='pitching_out_over_line',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mlbbovadaupcomingpitchers',
            name='pitching_out_under_line',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mlbbovadaupcomingpitchers',
            name='strikeout_over_line',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mlbbovadaupcomingpitchers',
            name='strikeout_under_line',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mlbbovadaupcomingpitchers',
            name='walks_over_line',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mlbbovadaupcomingpitchers',
            name='walks_under_line',
            field=models.FloatField(blank=True, null=True),
        ),
    ]