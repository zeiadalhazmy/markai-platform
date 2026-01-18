<template>
  <div class="card p18">
    <div class="row-between">
      <div>
        <h1 class="h1">الرئيسية (عميل)</h1>
        <div class="muted">تصفّح المنتجات — اطلب — تابع الطلبات</div>
      </div>
      <router-link class="btn btn-primary" to="/client/products">ابدأ</router-link>
    </div>

    <div class="grid2" style="margin-top:16px;">
      <div class="card p18" style="box-shadow:none;">
        <h2 class="h2">منتجات مميزة</h2>
        <div class="muted">عرض المنتجات من الـ API.</div>
      </div>

      <div class="card p18" style="box-shadow:none;">
        <h2 class="h2">طلباتي</h2>
        <div class="muted">عرض حالة الطلبات + تتبع.</div>
      </div>
    </div>
  </div>
</template>
