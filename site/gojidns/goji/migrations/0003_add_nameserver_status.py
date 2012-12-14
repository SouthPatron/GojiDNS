# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'NameserverStatus.resolving'
        db.add_column('goji_nameserverstatus', 'resolving',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'NameserverStatus.resolving'
        db.delete_column('goji_nameserverstatus', 'resolving')


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
        'goji.nameserverstatus': {
            'Meta': {'object_name': 'NameserverStatus'},
            'heartbeat': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'hostname': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '253'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'resolving': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
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