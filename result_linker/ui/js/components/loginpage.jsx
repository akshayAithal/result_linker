import React from 'react';
import {
    Form, Icon, Input, Button, Checkbox, notification
} from 'antd';
import axios from 'axios';

const axiosInstance = axios.create({
    //baseURL: '/',
    baseURL: window.location.href ,
  });

export class LoginPage extends React.Component {
    // https://ant.design/components/form/
    handleSubmit = (e) => {
        e.preventDefault();
        this.props.form.validateFields((err, values) => {
            if (!err) {
                axiosInstance.post("/login", {
                    username: values["userName"],
                    password: values["password"],
                    remember_me: values["remember"]
                })
                .then(function (response){
                    console.log(response);
                    notification["success"]({
                        message: "Success!",
                        description: `Logged in as ${values['userName']}!`
                    });
                })
                .catch(function (error) {
                    console.log(error);
                    notification["error"]({
                        message: "Error!",
                        description: `Unable to login as ${values['userName']}!`
                    })
                })

            }
        });
    }

    render() {
        const form = this.props.form;
        const { getFieldDecorator } = this.props.form;
        return (
            <Form onSubmit={(e) => this.props.handleLogin(e, form)} className="login-form">
                <Form.Item>
                    {getFieldDecorator('userName', {
                        rules: [{ required: true, message: 'Please input your username!' }],
                    })(
                        <Input
                            style={{ resize: "none", height: "2rem",  }}
                            prefix={<Icon type="user" style={{ color: 'rgba(0,0,0,.25)' }} />}
                            placeholder="Redmine Username" />
                            )}
                </Form.Item>
                <Form.Item>
                    {getFieldDecorator('password', {
                        rules: [{ required: true, message: 'Please input your Password!' }],
                    })(
                        <Input
                            style={{resize: "none", height: "2rem", }}
                            prefix={<Icon type="lock" style={{ color: 'rgba(0,0,0,.25)' }} />}
                            type="password"
                            placeholder="Redmine Password" />
                    )}
                </Form.Item>
                <Form.Item>
                    {getFieldDecorator('remember', {
                        valuePropName: 'checked',
                        initialValue: true,
                    })(
                        <Checkbox>Remember me</Checkbox>
                    )}
                    <Button type="primary" htmlType="submit" className="login-form-button">
                        Log in
                    </Button>
                </Form.Item>
            </Form>
        );
    }
}
