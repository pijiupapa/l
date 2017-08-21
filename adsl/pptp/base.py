# -*- coding=utf-8 -*-
import redis


class VpnConnectionBase(object):

    DISCONNECT_STATE = 'disconnect'
    CONNECTED_STATE = 'connected'
    CONNECTING_STATE = 'conneting'

    def __init__(self, username, password, vpn_name, vpn_server):
        self.username = username
        self.password = password
        self.vpn_name = vpn_name
        self.vpn_server = vpn_server


    @property
    def status(self):
        if 'ppp0' in os.popen('ifconfig').read():
            return self.DISCONNECT_STATE
        return self.CONNECTED_STATE


    def connect(self):
        while True:
            if self.status == 'connected':
                logging.debug(u"vpn已经连接")
                break
            shell = 'pptpsetup --create %s --server %s --username %s --password %s --encrypt --start' % (self.vpn_name, self.vpn_server, self.username, self.password)
            os.system(shell)

            while True:
                ret = self.wait_pptp_status('connected')
                if ret:
                    return
                if self.status == 'disconnect':
                    logging.debug(u"vpn连接失败")
                    time.sleep(2)
                    break


    def wait_pptp_status(self, status, timeout=5):
        start_time = time.time()
        while True:
            if self.status == status:
                return True
            if time.time() - start_time > timeout:
                return False
            time.sleep(1)


    def close(self):
        if self.status == 'disconnect':
            logging.info(u"vpn的状态为已关闭, 不需要重新关闭")
            return
        logging.info(u"关闭vpn")
        shell = "pkill pppd"
        subprocess.call(shell, shell=True)
        self.wait_pptp_status('disconnect')



class VpnManagerBase(object):

    def __init__(self):
        pass

    def start(self):
        pass


    def add_default_route(self):
        pass


    def set_is_pptp(self, value):
        pass

    def get_ip_pptp(self):
        pass


    def set_vpn_ip(self, ip):
        pass


    @property
    def is_died(self):
        pass


    def check_died(self):
        pass


    def run(self):
        pass


    def random_choice(self):
        pass


    def reconnect(self):
        pass
