# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'AuthenticationCode'
        db.create_table('goji_authenticationcode', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('profile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['goji.Profile'])),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=16)),
        ))
        db.send_create_signal('goji', ['AuthenticationCode'])

        # Adding model 'EmailChangeRequest'
        db.create_table('goji_emailchangerequest', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('profile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['goji.Profile'])),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('old_address', self.gf('django.db.models.fields.EmailField')(max_length=254)),
            ('new_address', self.gf('django.db.models.fields.EmailField')(max_length=254)),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=16)),
        ))
        db.send_create_signal('goji', ['EmailChangeRequest'])

        # Adding model 'Profile'
        db.create_table('goji_profile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(related_name='goji_profile', unique=True, to=orm['auth.User'])),
            ('dob', self.gf('django.db.models.fields.DateField')(default=None, null=True)),
            ('gender', self.gf('django.db.models.fields.IntegerField')(default=None, null=True)),
            ('country', self.gf('django.db.models.fields.CharField')(default=None, max_length=2, null=True)),
            ('timezone', self.gf('django.db.models.fields.CharField')(default='UTC', max_length=64)),
            ('website', self.gf('django.db.models.fields.CharField')(default=None, max_length=255, null=True)),
            ('location', self.gf('django.db.models.fields.CharField')(default=None, max_length=255, null=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(default=None, max_length=255, null=True)),
        ))
        db.send_create_signal('goji', ['Profile'])

        # Adding model 'Domain'
        db.create_table('goji_domain', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('profile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['goji.Profile'])),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=253)),
            ('is_master', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('primary', self.gf('django.db.models.fields.CharField')(max_length=253)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=254)),
            ('ttl', self.gf('django.db.models.fields.IntegerField')(default=7200)),
            ('refresh', self.gf('django.db.models.fields.IntegerField')(default=None, null=True)),
            ('retry', self.gf('django.db.models.fields.IntegerField')(default=None, null=True)),
            ('expire', self.gf('django.db.models.fields.IntegerField')(default=None, null=True)),
        ))
        db.send_create_signal('goji', ['Domain'])

        # Adding model 'Resource'
        db.create_table('goji_resource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('domain', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['goji.Domain'])),
            ('resource_type', self.gf('django.db.models.fields.IntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(default=None, max_length=253, null=True)),
            ('value', self.gf('django.db.models.fields.CharField')(default=None, max_length=253, null=True)),
            ('preference', self.gf('django.db.models.fields.IntegerField')(default=None, null=True)),
            ('ttl', self.gf('django.db.models.fields.IntegerField')(default=None, null=True)),
            ('protocol', self.gf('django.db.models.fields.IntegerField')(default=None, null=True)),
            ('port', self.gf('django.db.models.fields.IntegerField')(default=None, null=True)),
            ('weight', self.gf('django.db.models.fields.IntegerField')(default=None, null=True)),
            ('static', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('goji', ['Resource'])


    def backwards(self, orm):
        # Deleting model 'AuthenticationCode'
        db.delete_table('goji_authenticationcode')

        # Deleting model 'EmailChangeRequest'
        db.delete_table('goji_emailchangerequest')

        # Deleting model 'Profile'
        db.delete_table('goji_profile')

        # Deleting model 'Domain'
        db.delete_table('goji_domain')

        # Deleting model 'Resource'
        db.delete_table('goji_resource')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'goji.authenticationcode': {
            'Meta': {'object_name': 'AuthenticationCode'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '16'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['goji.Profile']"})
        },
        'goji.domain': {
            'Meta': {'ordering': "['name']", 'object_name': 'Domain'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '254'}),
            'expire': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_master': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '253'}),
            'primary': ('django.db.models.fields.CharField', [], {'max_length': '253'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['goji.Profile']"}),
            'refresh': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True'}),
            'retry': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'ttl': ('django.db.models.fields.IntegerField', [], {'default': '7200'})
        },
        'goji.emailchangerequest': {
            'Meta': {'object_name': 'EmailChangeRequest'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '16'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'new_address': ('django.db.models.fields.EmailField', [], {'max_length': '254'}),
            'old_address': ('django.db.models.fields.EmailField', [], {'max_length': '254'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['goji.Profile']"})
        },
        'goji.profile': {
            'Meta': {'object_name': 'Profile'},
            'country': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '2', 'null': 'True'}),
            'dob': ('django.db.models.fields.DateField', [], {'default': 'None', 'null': 'True'}),
            'gender': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'null': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'null': 'True'}),
            'timezone': ('django.db.models.fields.CharField', [], {'default': "'UTC'", 'max_length': '64'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'goji_profile'", 'unique': 'True', 'to': "orm['auth.User']"}),
            'website': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'null': 'True'})
        },
        'goji.resource': {
            'Meta': {'ordering': "['-static', 'preference', 'name', 'value']", 'object_name': 'Resource'},
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['goji.Domain']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '253', 'null': 'True'}),
            'port': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True'}),
            'preference': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True'}),
            'protocol': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True'}),
            'resource_type': ('django.db.models.fields.IntegerField', [], {}),
            'static': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ttl': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '253', 'null': 'True'}),
            'weight': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True'})
        }
    }

    complete_apps = ['goji']