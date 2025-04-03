from django.contrib import admin

from .models import ContactInfo, Violation, ViolationType, Waiter, ViolationWaiter
from .models import Post
from .models import ViolationStatus


@admin.register(ViolationStatus)
class ViolationStatusAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)
    ordering = ('name',)
    prepopulated_fields = {}

    fieldsets = (
        (None, {
            'fields': ('name',)
        }),
    )


@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ('email', 'phone', 'address', 'created_at', 'updated_at')
    search_fields = ('email', 'phone', 'address')
    list_filter = ('created_at', 'updated_at')
    ordering = ('email',)
    readonly_fields = ('created_at', 'updated_at')  # Исправлено здесь

    fieldsets = (
        (None, {
            'fields': ('email', 'phone', 'address')
        }),
        ('Даты', {
            'fields' : ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'salary', 'experience_required', 'created_at', 'updated_at')
    search_fields = ('title', 'description')
    list_filter = ('experience_required', 'created_at', 'updated_at')
    ordering = ('title',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ("Основная информация", {
            'fields'     : ('title', 'description', 'salary', 'experience_required'),
            'description': "Основные данные о должности"
        }),
        ("Даты", {
            'fields'     : ('created_at', 'updated_at'),
            'classes'    : ('collapse',),
            'description': "Системные даты создания и изменения записи"
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields
        return ()

@admin.register(Violation)
class ViolationAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'violation_type', 'status', 'get_waiters')
    search_fields = ('note', 'violation_type__name', 'status__name')
    list_filter = ('date', 'violation_type', 'status')
    ordering = ('-date',)
    readonly_fields = ('date',)

    fieldsets = (
        ("Основная информация", {
            'fields': ('image', 'note', 'date'),
            'description': "Основные данные о нарушении"
        }),
        ("Связанные данные", {
            'fields': ('violation_type', 'status'),
            'description': "Тип и состояние нарушения"
        }),
    )

    def get_waiters(self, obj):
        """Возвращает строку с официантами, связанными с нарушением."""
        waiters = obj.violation_waiters.all()
        return ", ".join([f"{vw.waiter} ({vw.role})" for vw in waiters])
    get_waiters.short_description = 'Официанты'

    def get_readonly_fields(self, request, obj=None):
        """Делаем дату неизменяемой даже при создании объекта"""
        if obj:  # При редактировании существующего объекта
            return self.readonly_fields
        return ()  # При создании нового объекта разрешаем авто-заполнение

@admin.register(ViolationType)
class ViolationTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')
    list_filter = ('name',)
    ordering = ('name',)
    prepopulated_fields = {}

    fieldsets = (
        (None, {
            'fields'     : ('name', 'description'),
            'description': "Основные данные о типе нарушения"
        }),
    )





@admin.register(Waiter)
class WaiterAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'patronymic', 'user_id', 'has_access', 'created_at', 'updated_at')
    search_fields = ('last_name', 'first_name', 'patronymic', 'user_id')
    list_filter = ('posts', 'has_access', 'created_at', 'updated_at')  # Добавили фильтр по доступу
    ordering = ('last_name', 'first_name')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('posts',)

    fieldsets = (
        ("Основная информация", {
            'fields'     : ('user_id', 'image', 'first_name', 'last_name', 'patronymic', 'has_access'),
            'description': "Основные данные об официанте"
        }),
        ("Должности и контактная информация", {
            'fields'     : ('posts', 'contact_info'),
            'description': "Связь с должностями и контактной информацией"
        }),
        ("Системные данные", {
            'fields'     : ('created_at', 'updated_at'),
            'classes'    : ('collapse',),
            'description': "Системные даты создания и обновления записи"
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields
        return ()


@admin.register(ViolationWaiter)
class ViolationWaiterAdmin(admin.ModelAdmin):
    list_display = ('violation', 'waiter', 'role')
    list_filter = ('role',)
    search_fields = ('violation__id', 'waiter__last_name')