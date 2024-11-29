<div id="staffModules" class="module">
    <h2>工作人员功能</h2>
    <button>信息录入</button>
    <button>证件制作</button>
    <button>证件分发</button>
    <button>用车管理</button>
    <button>信息查看</button>

    <div id="infoEntry" class="module">
        <h2>信息录入</h2>
        <form>
            <label for="guest_id">嘉宾ID:</label>
            <input type="text" id="guest_id" name="guest_id"><br><br>
            
            <label for="name">姓名:</label>
            <input type="text" id="name" name="name"><br><br>
            
            <label for="organization">单位:</label>
            <input type="text" id="organization" name="organization"><br><br>
            
            <label for="position">职务:</label>
            <input type="text" id="position" name="position"><br><br>
            
            <label for="contact">联系方式:</label>
            <input type="text" id="contact" name="contact"><br><br>
            
            <input type="submit" value="提交">
        </form>
    </div>

    <div id="badgeCreation" class="module">
        <h2>证件制作</h2>
        <form>
            <label for="guest_id">嘉宾ID:</label>
            <input type="text" id="guest_id" name="guest_id"><br><br>
            
            <label for="badge_type">证件类型:</label>
            <input type="text" id="badge_type" name="badge_type"><br><br>
            
            <input type="submit" value="制作证件">
        </form>
    </div>

    <div id="badgeDistribution" class="module">
        <h2>证件分发</h2>
        <form>
            <label for="badge_id">证件ID:</label>
            <input type="text" id="badge_id" name="badge_id"><br><br>
            
            <label for="guest_id">嘉宾ID:</label>
            <input type="text" id="guest_id" name="guest_id"><br><br>
            
            <input type="submit" value="分发证件">
        </form>
    </div>

    <div id="vehicleManagement" class="module">
        <h2>用车管理</h2>
        <form>
            <label for="guest_id">嘉宾ID:</label>
            <input type="text" id="guest_id" name="guest_id"><br><br>
            
            <label for="vehicle_type">车辆类型:</label>
            <input type="text" id="vehicle_type" name="vehicle_type"><br><br>
            
            <label for="use_time">用车时间:</label>
            <input type="datetime-local" id="use_time" name="use_time"><br><br>
            
            <input type="submit" value="安排用车">
        </form>
    </div>

    <div id="infoView" class="module">
        <h2>信息查看</h2>
        <p>嘉宾ID: 12345</p>
        <p>姓名: 张三</p>
        <p>单位: 某某公司</p>
        <p>职务: 总经理</p>
        <p>联系方式: 123-456-7890</p>
    </div>
</div>